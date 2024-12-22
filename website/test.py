import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy.signal import find_peaks


# Load the dataset
file_path = 'DummyData/Single Leg Hop 100Hz Raw Accel.xlsx'
data = pd.read_excel(file_path)

# Extract relevant columns for Accelerometer 1, 2, and 3
local_accel_1 = data[['accelx_1', 'accely_1', 'Accelz_1']].to_numpy()
quaternions_1 = data[['quat_w1', 'quat_x1', 'quat_y1', 'quat_z1']].to_numpy()

local_accel_2 = data[['accelx_2', 'accely_2', 'Accelz_2']].to_numpy()
quaternions_2 = data[['quat_w1.1', 'quat_x1.1', 'quat_y1.1', 'quat_z1.1']].to_numpy()

local_accel_3 = data[['accelx_3', 'accely_3', 'Accelz_3']].to_numpy()
quaternions_3 = data[['quat_w1.2', 'quat_x1.2', 'quat_y1.2', 'quat_z1.2']].to_numpy()

timestamps = data['Timestamp'].to_numpy()  # Time in milliseconds

# Calculate acceleration magnitude
def calculate_magnitude(global_accel):
    return np.sqrt(np.sum(global_accel**2, axis=1))

# Classify points as grounded or airborne
def classify_gravity_effect(accel_magnitude, gravity=9.81, threshold=0.1):
    lower_bound = gravity * (1 - threshold)
    upper_bound = gravity * (1 + threshold)
    is_grounded = (accel_magnitude >= lower_bound) & (accel_magnitude <= upper_bound)
    return is_grounded

# Normalize quaternions
def normalize_quaternions(quaternions):
    norms = np.linalg.norm(quaternions, axis=1, keepdims=True)
    norms[norms == 0] = 1  # Prevent division by zero
    return quaternions / norms

# Apply matrix-based rotation using quaternions
def quaternion_to_rotation_matrix(quaternion):
    w, x, y, z = quaternion
    R = np.array([
        [1 - 2 * (y**2 + z**2), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x**2 + z**2), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x**2 + y**2)]
    ])
    return R


def rotate_to_global_matrix(local_accel, quaternions):
    num_samples = local_accel.shape[0]
    global_accel = np.zeros_like(local_accel)
    for i in range(num_samples):
        R = quaternion_to_rotation_matrix(quaternions[i])
        global_accel[i, :] = np.dot(R, local_accel[i, :])
    return global_accel

# Kalman filter implementation with safeguards
def adaptive_kalman_filter(accel, time):
    dt = np.mean(np.diff(time))  # Time step
    if dt <= 0:
        raise ValueError("Invalid time step detected.")
    
    state = np.zeros(2)  # [position, velocity]
    F = np.array([[1, dt], [0, 1]])
    B = np.array([[0.5 * dt**2], [dt]])
    H = np.array([[0, 1]])
    P = np.eye(2)
    Q = np.array([[1e-5, 0], [0, 1e-5]])  # Initial process noise covariance
    R = np.array([[1e-3]])  # Initial measurement noise covariance
    position = []
    velocity = []

    accel = np.nan_to_num(accel, nan=0.0, posinf=0.0, neginf=0.0)  # Handle invalid acceleration values

    for i, a in enumerate(accel):
        if i > 1:
            Q *= np.abs(a) * 0.01  # Adjust process noise
            R *= np.var(accel[:i]) * 0.01  # Adjust measurement noise
            Q = np.clip(Q, 1e-10, 1e-2)  # Clamp Q values
            R = np.clip(R, 1e-10, 1e-2)  # Clamp R values

        # Prediction
        state = F @ state + B.flatten() * a
        P = F @ P @ F.T + Q

        # Update
        z = np.array([[a]])
        y = z - H @ state
        S = H @ P @ H.T + R
        S += np.eye(S.shape[0]) * 1e-6  # Regularization

        if np.all(np.isfinite(S)) and np.linalg.cond(S) < 1 / np.finfo(S.dtype).eps:
            K = P @ H.T @ np.linalg.inv(S)
            state = state + (K @ y).flatten()
            P = P - K @ H @ P
        else:
            print(f"Skipping update at index {i} due to invalid or poorly conditioned S.")
        
        position.append(state[0])
        velocity.append(state[1])

    return np.array(position), np.array(velocity)

# Complementary filter
def complementary_filter(accel, alpha=0.98):
    """
    Apply a complementary filter to accelerometer data.
    
    Parameters:
        accel (numpy.ndarray): Nx3 array of raw accelerometer data.
        alpha (float): Smoothing factor. (0 < alpha < 1)
                      Higher alpha retains more high-frequency components.
                      
    Returns:
        filtered_accel (numpy.ndarray): Nx3 array of filtered accelerometer data.
    """
    filtered_accel = np.zeros_like(accel)
    filtered_accel[0, :] = accel[0, :]  # Initialize with the first data point
    
    for i in range(1, accel.shape[0]):
        filtered_accel[i, :] = alpha * filtered_accel[i - 1, :] + (1 - alpha) * accel[i, :]
    
    return filtered_accel



# Calculate pitch, roll, and yaw from quaternions
def calculate_euler_angles(quaternions):
    roll = np.arctan2(2 * (quaternions[:, 0] * quaternions[:, 1] + quaternions[:, 2] * quaternions[:, 3]),
                      1 - 2 * (quaternions[:, 1]**2 + quaternions[:, 2]**2))
    pitch = np.arcsin(2 * (quaternions[:, 0] * quaternions[:, 2] - quaternions[:, 3] * quaternions[:, 1]))
    yaw = np.arctan2(2 * (quaternions[:, 0] * quaternions[:, 3] + quaternions[:, 1] * quaternions[:, 2]),
                     1 - 2 * (quaternions[:, 2]**2 + quaternions[:, 3]**2))
    return np.degrees(roll), np.degrees(pitch), np.degrees(yaw)


##DOESNT WORK YET
def identify_airborne_time(accelerations, threshold=3.0):
    """
    Identifies airborne time periods based on average acceleration magnitude.

    Parameters:
        accelerations (list of numpy.ndarray): List containing Nx3 arrays of accelerations for all accelerometers.
        threshold (float): Threshold for the magnitude of acceleration to consider as "airborne".

    Returns:
        average_magnitude (numpy.ndarray): Average magnitude of acceleration.
        airborne_times (numpy.ndarray): Boolean array indicating airborne states (True for airborne, False otherwise).
    """
    # Step 1: Compute the magnitude of acceleration for each accelerometer
    magnitudes = [np.linalg.norm(accel, axis=1) for accel in accelerations]
    
    # Step 2: Compute the average magnitude across all accelerometers
    average_magnitude = np.mean(magnitudes, axis=0)
    
    # Step 3: Determine airborne states
    airborne_times = average_magnitude < threshold
    
    return average_magnitude, airborne_times

def check_gravity_alignment(aligned_accel, time_seconds, accelerometer_name):
    """
    Perform checks and visualizations to verify gravity alignment.

    Parameters:
        aligned_accel (numpy.ndarray): Nx3 array of gravity-aligned accelerations.
        time_seconds (numpy.ndarray): Time array corresponding to accelerations.
        accelerometer_name (str): Name of the accelerometer for labeling.
    """
    # Step 1: Calculate the average Z acceleration
    avg_z_accel = np.mean(aligned_accel[:, 2])
    print(f"Average Z-Acceleration ({accelerometer_name}): {avg_z_accel:.2f} m/s² (Expected: ~-9.81 m/s²)")

    # Step 2: Plot the aligned accelerations for verification
    plt.figure(figsize=(12, 6))
    plt.plot(time_seconds, aligned_accel[:, 0], label="X-Axis Acceleration", color="blue")
    plt.plot(time_seconds, aligned_accel[:, 1], label="Y-Axis Acceleration", color="green")
    plt.plot(time_seconds, aligned_accel[:, 2], label="Z-Axis Acceleration (Gravity)", color="red")
    plt.axhline(-9.81, color="black", linestyle="--", label="Expected Gravity (-9.81 m/s²)")
    plt.title(f"Gravity Alignment Check - {accelerometer_name}")
    plt.xlabel("Time (s)")
    plt.ylabel("Acceleration (m/s²)")
    plt.legend()
    plt.grid()
    plt.show()

def calibrate_and_align_gravity_with_custom_axes(global_accel, samples=50):
    """
    Calibrate and align global accelerations such that:
    - Gravity aligns with the negative Y-axis.
    - Forward aligns with the positive X-axis.
    - Side aligns with the positive Z-axis.

    Parameters:
        global_accel (numpy.ndarray): Nx3 array of global accelerations (X, Y, Z).
        samples (int): Number of initial samples to average for gravity estimation.

    Returns:
        aligned_accel (numpy.ndarray): Nx3 array of custom-aligned accelerations.
        gravity_direction (numpy.ndarray): Unit vector representing the direction of gravity.
    """
    # Step 1: Compute average gravity direction from initial samples
    gravity_vector = np.mean(global_accel[:samples], axis=0)
    gravity_unit = gravity_vector / np.linalg.norm(gravity_vector)

    # Step 2: Define the target negative Y-axis for gravity
    target_y_axis = np.array([0, -1, 0])  # Gravity points to negative Y-axis

    # Step 3: Compute the rotation matrix to align gravity with the target negative Y-axis
    cross_prod = np.cross(gravity_unit, target_y_axis)
    dot_prod = np.dot(gravity_unit, target_y_axis)

    if np.linalg.norm(cross_prod) == 0:
        # If already aligned, return identity matrix
        rotation_matrix = np.eye(3)
    else:
        cross_prod /= np.linalg.norm(cross_prod)
        skew_sym_matrix = np.array([
            [0, -cross_prod[2], cross_prod[1]],
            [cross_prod[2], 0, -cross_prod[0]],
            [-cross_prod[1], cross_prod[0], 0]
        ])
        rotation_matrix = (
            np.eye(3) +
            skew_sym_matrix +
            np.matmul(skew_sym_matrix, skew_sym_matrix) * ((1 - dot_prod) / (np.linalg.norm(cross_prod) ** 2))
        )

    # Step 4: Apply rotation to align data
    aligned_accel = np.dot(global_accel, rotation_matrix.T)

    return aligned_accel, gravity_unit


#Local Minimum Calculation
def find_two_local_minima(pitch_data, time_data, window_size=50):
    """
    Identify two local minima on the pitch data ensuring they are the smallest within the nearest window.

    Parameters:
        pitch_data (numpy.ndarray): Array of pitch angles (degrees).
        time_data (numpy.ndarray): Array of time values (seconds).
        window_size (int): Number of samples around the minima to check for uniqueness.

    Returns:
        minima_indices (list): Indices of the two identified local minima.
    """
    # Find all local minima
    inverted_pitch_data = -pitch_data
    all_minima, _ = find_peaks(inverted_pitch_data)

    # Validate minima within the given window
    validated_minima = []
    for minimum in all_minima:
        start = max(0, minimum - window_size)
        end = min(len(pitch_data), minimum + window_size)
        local_window = pitch_data[start:end]
        if pitch_data[minimum] == np.min(local_window):
            validated_minima.append(minimum)

    # Ensure only two minima are returned
    if len(validated_minima) < 2:
        raise ValueError("Not enough valid local minima found.")
    validated_minima = sorted(validated_minima[:2])

    # Plot the pitch data with the identified minima
    plt.figure(figsize=(12, 6))
    plt.plot(time_data, pitch_data, label="Pitch Data", color="black")
    for idx, minimum in enumerate(validated_minima):
        plt.scatter(time_data[minimum], pitch_data[minimum], label=f"Local Minimum {idx + 1}", color=["red", "blue"][idx], zorder=5)

    plt.title("Pitch Data with Local Minima")
    plt.xlabel("Time (s)")
    plt.ylabel("Pitch (degrees)")
    plt.legend()
    plt.grid()
    plt.show()

    return validated_minima

# Normalize quaternions
quaternions_1 = normalize_quaternions(quaternions_1)
quaternions_2 = normalize_quaternions(quaternions_2)
quaternions_3 = normalize_quaternions(quaternions_3)

# Convert timestamps to seconds
time_seconds = (timestamps - timestamps[0]) / 1000.0

# Rotate accelerations to global frame
global_accel_1 = rotate_to_global_matrix(local_accel_1, quaternions_1)
global_accel_2 = rotate_to_global_matrix(local_accel_2, quaternions_2)
global_accel_3 = rotate_to_global_matrix(local_accel_3, quaternions_3)

# Calibrate and align gravity
aligned_accel_1, gravity_dir_1 = calibrate_and_align_gravity_with_custom_axes(global_accel_1)
aligned_accel_2, gravity_dir_2 = calibrate_and_align_gravity_with_custom_axes(global_accel_2)
aligned_accel_3, gravity_dir_3 = calibrate_and_align_gravity_with_custom_axes(global_accel_3)

# Rotate accelerations to global frame
aligned_accel_1 = complementary_filter(aligned_accel_1)
aligned_accel_2 = complementary_filter(aligned_accel_2)
aligned_accel_3 = complementary_filter(aligned_accel_3)

# Apply Kalman filter for position and velocity
positions_1, velocities_1 = [], []
positions_2, velocities_2 = [], []
positions_3, velocities_3 = [], []
for axis in range(3):  # X, Y, Z
    pos_1, vel_1 = adaptive_kalman_filter(aligned_accel_1[:, axis], time_seconds)
    pos_2, vel_2 = adaptive_kalman_filter(aligned_accel_2[:, axis], time_seconds)
    pos_3, vel_3 = adaptive_kalman_filter(aligned_accel_3[:, axis], time_seconds)
    positions_1.append(pos_1)
    velocities_1.append(vel_1)
    positions_2.append(pos_2)
    velocities_2.append(vel_2)
    positions_3.append(pos_3)
    velocities_3.append(vel_3)

positions_1 = np.array(positions_1).T
velocities_1 = np.array(velocities_1).T
positions_2 = np.array(positions_2).T
velocities_2 = np.array(velocities_2).T
positions_3 = np.array(positions_3).T
velocities_3 = np.array(velocities_3).T

# Calculate Euler angles for all accelerometers
roll_1, pitch_1, yaw_1 = calculate_euler_angles(quaternions_1)
roll_2, pitch_2, yaw_2 = calculate_euler_angles(quaternions_2)
roll_3, pitch_3, yaw_3 = calculate_euler_angles(quaternions_3)




# Compute relative pitch, roll, and yaw for top and bottom accelerometers
relative_pitch_1 = pitch_1 - pitch_1[0]
relative_roll_1 = roll_1 - roll_1[0]
relative_yaw_1 = yaw_1 - yaw_1[0]

relative_pitch_3 = pitch_3 - pitch_3[0]
relative_roll_3 = roll_3 - roll_3[0]
relative_yaw_3 = yaw_3 - yaw_3[0]

# Compute overall relative Euler angles
relative_pitch = 180 - (relative_pitch_1 - relative_pitch_3)
relative_roll = 180 - (relative_roll_1 - relative_roll_3)


# Compute acceleration magnitudes for all accelerometers
magnitude_1 = calculate_magnitude(aligned_accel_1)
magnitude_2 = calculate_magnitude(aligned_accel_2)
magnitude_3 = calculate_magnitude(aligned_accel_3)

# Classify points
grounded_1 = classify_gravity_effect(magnitude_1)
grounded_2 = classify_gravity_effect(magnitude_2)
grounded_3 = classify_gravity_effect(magnitude_3)

# Combine the accelerations into a list
accelerations = [aligned_accel_1, aligned_accel_2, aligned_accel_3]

# Identify airborne times
airborne_times = identify_airborne_time(accelerations)

phases = find_two_local_minima(relative_pitch, time_seconds)
print(phases)

# Check gravity alignment for each accelerometer
check_gravity_alignment(aligned_accel_1, time_seconds, "Accelerometer 1")
check_gravity_alignment(aligned_accel_2, time_seconds, "Accelerometer 2")
check_gravity_alignment(aligned_accel_3, time_seconds, "Accelerometer 3")

# Validation plot
plt.figure(figsize=(10, 6))
plt.plot(time_seconds, aligned_accel_1[:, 1], label='Aligned -Y (Accel 1)')
plt.plot(time_seconds, aligned_accel_2[:, 1], label='Aligned -Y (Accel 2)')
plt.plot(time_seconds, aligned_accel_3[:, 1], label='Aligned -Y (Accel 3)')
plt.axhline(-9.81, color='r', linestyle='--', label='Expected Gravity (-9.81 m/s²)')
plt.title('Gravity Alignment Validation (Negative Y)')
plt.xlabel('Time (s)')
plt.ylabel('Acceleration (m/s²)')
plt.legend()
plt.grid()
plt.show()

# Save visualizations as a PDF
output_pdf = 'Calibrated_Acceleration_Velocity_Position_All_Accelerometers.pdf'

with PdfPages(output_pdf) as pdf:
    plt.figure(figsize=(14, 90))  # Adjust figure size to accommodate all graphs

    # Accelerometer 1 (Top): Acceleration
    plt.subplot(16, 1, 1)
    plt.plot(time_seconds, aligned_accel_1[:, 0], label="X Accel (Top)")
    plt.plot(time_seconds, aligned_accel_1[:, 1], label="Y Accel (Top)")
    plt.plot(time_seconds, aligned_accel_1[:, 2], label="Z Accel (Top)")
    plt.title("Time vs Acceleration (Accelerometer 1 - Top)")
    plt.xlabel("Time (s)")
    plt.ylabel("Acceleration (m/s²)")
    plt.legend()

    # Accelerometer 1 (Top): Velocity
    plt.subplot(16, 1, 2)
    plt.plot(time_seconds, velocities_1[:, 0], label="X Velocity (Top)")
    plt.plot(time_seconds, velocities_1[:, 1], label="Y Velocity (Top)")
    plt.plot(time_seconds, velocities_1[:, 2], label="Z Velocity (Top)")
    plt.title("Time vs Velocity (Accelerometer 1 - Top)")
    plt.xlabel("Time (s)")
    plt.ylabel("Velocity (m/s)")
    plt.legend()

    # Accelerometer 1 (Top): Position
    plt.subplot(16, 1, 3)
    plt.plot(time_seconds, positions_1[:, 0], label="X Position (Top)")
    plt.plot(time_seconds, positions_1[:, 1], label="Y Position (Top)")
    plt.plot(time_seconds, positions_1[:, 2], label="Z Position (Top)")
    plt.title("Time vs Position (Accelerometer 1 - Top)")
    plt.xlabel("Time (s)")
    plt.ylabel("Position (m)")
    plt.legend()

    # Accelerometer 2 (Bottom): Acceleration
    plt.subplot(16, 1, 4)
    plt.plot(time_seconds, aligned_accel_2[:, 0], label="X Accel (Bottom)")
    plt.plot(time_seconds, aligned_accel_2[:, 1], label="Y Accel (Bottom)")
    plt.plot(time_seconds, aligned_accel_2[:, 2], label="Z Accel (Bottom)")
    plt.title("Time vs Acceleration (Accelerometer 2 - Bottom)")
    plt.xlabel("Time (s)")
    plt.ylabel("Acceleration (m/s²)")
    plt.legend()

    # Accelerometer 2 (Bottom): Velocity
    plt.subplot(16, 1, 5)
    plt.plot(time_seconds, velocities_2[:, 0], label="X Velocity (Bottom)")
    plt.plot(time_seconds, velocities_2[:, 1], label="Y Velocity (Bottom)")
    plt.plot(time_seconds, velocities_2[:, 2], label="Z Velocity (Bottom)")
    plt.title("Time vs Velocity (Accelerometer 2 - Bottom)")
    plt.xlabel("Time (s)")
    plt.ylabel("Velocity (m/s)")
    plt.legend()

    # Accelerometer 2 (Bottom): Position
    plt.subplot(16, 1, 6)
    plt.plot(time_seconds, positions_2[:, 0], label="X Position (Bottom)")
    plt.plot(time_seconds, positions_2[:, 1], label="Y Position (Bottom)")
    plt.plot(time_seconds, positions_2[:, 2], label="Z Position (Bottom)")
    plt.title("Time vs Position (Accelerometer 2 - Bottom)")
    plt.xlabel("Time (s)")
    plt.ylabel("Position (m)")
    plt.legend()

    # Accelerometer 3 (Middle): Acceleration
    plt.subplot(16, 1, 7)
    plt.plot(time_seconds, aligned_accel_3[:, 0], label="X Accel (Middle)")
    plt.plot(time_seconds, aligned_accel_3[:, 1], label="Y Accel (Middle)")
    plt.plot(time_seconds, aligned_accel_3[:, 2], label="Z Accel (Middle)")
    plt.title("Time vs Acceleration (Accelerometer 3 - Middle)")
    plt.xlabel("Time (s)")
    plt.ylabel("Acceleration (m/s²)")
    plt.legend()

    # Accelerometer 3 (Middle): Velocity
    plt.subplot(16, 1, 8)
    plt.plot(time_seconds, velocities_3[:, 0], label="X Velocity (Middle)")
    plt.plot(time_seconds, velocities_3[:, 1], label="Y Velocity (Middle)")
    plt.plot(time_seconds, velocities_3[:, 2], label="Z Velocity (Middle)")
    plt.title("Time vs Velocity (Accelerometer 3 - Middle)")
    plt.xlabel("Time (s)")
    plt.ylabel("Velocity (m/s)")
    plt.legend()

    # Accelerometer 3 (Middle): Position
    plt.subplot(16, 1, 9)
    plt.plot(time_seconds, positions_3[:, 0], label="X Position (Middle)")
    plt.plot(time_seconds, positions_3[:, 1], label="Y Position (Middle)")
    plt.plot(time_seconds, positions_3[:, 2], label="Z Position (Middle)")
    plt.title("Time vs Position (Accelerometer 3 - Middle)")
    plt.xlabel("Time (s)")
    plt.ylabel("Position (m)")
    plt.legend()

     # Relative Pitch
    plt.subplot(16, 1, 10)
    plt.plot(time_seconds, relative_pitch, label="Relative Pitch")
    plt.title("Time vs Relative Pitch")
    plt.xlabel("Time (s)")
    plt.ylabel("Pitch (degrees)")
    plt.legend()

    # Relative Roll
    plt.subplot(16, 1, 11)
    plt.plot(time_seconds, relative_roll, label="Relative Roll")
    plt.title("Time vs Relative Roll")
    plt.xlabel("Time (s)")
    plt.ylabel("Roll (degrees)")
    plt.legend()

    plt.subplot(16, 1, 12)
    plt.plot(time_seconds, magnitude_1, label="Acceleration Magnitude (Accel 1)")
    plt.scatter(time_seconds[~grounded_1], magnitude_1[~grounded_1], color='r', label="Airborne", s=10)
    plt.axhline(9.81, color='g', linestyle='--', label="Gravity")
    plt.title("Acceleration Magnitude - Accelerometer 1")
    plt.xlabel("Time (s)")
    plt.ylabel("Magnitude (m/s²)")
    plt.legend()

    # Plot acceleration magnitude for Accelerometer 2
    plt.subplot(16, 1, 13)
    plt.plot(time_seconds, magnitude_2, label="Acceleration Magnitude (Accel 2)")
    plt.scatter(time_seconds[~grounded_2], magnitude_2[~grounded_2], color='r', label="Airborne", s=10)
    plt.axhline(9.81, color='g', linestyle='--', label="Gravity")
    plt.title("Acceleration Magnitude - Accelerometer 2")
    plt.xlabel("Time (s)")
    plt.ylabel("Magnitude (m/s²)")
    plt.legend()

    # Plot acceleration magnitude for Accelerometer 3
    plt.subplot(16, 1, 14)
    plt.plot(time_seconds, magnitude_3, label="Acceleration Magnitude (Accel 3)")
    plt.scatter(time_seconds[~grounded_3], magnitude_3[~grounded_3], color='r', label="Airborne", s=10)
    plt.axhline(9.81, color='g', linestyle='--', label="Gravity")
    plt.title("Acceleration Magnitude - Accelerometer 3")
    plt.xlabel("Time (s)")
    plt.ylabel("Magnitude (m/s²)")
    plt.legend()

    # Add a new subplot for airborne detection
    plt.subplot(16, 1, 15)  # Add as the 13th subplot in the figure
    average_magnitude, airborne_times = identify_airborne_time(
        [aligned_accel_1, aligned_accel_2, aligned_accel_3],
        threshold=3.0
    )
    plt.plot(time_seconds, average_magnitude, label="Average Acceleration", color="blue")
    plt.scatter(time_seconds[airborne_times], average_magnitude[airborne_times], 
               color="red", label="Airborne", s=10)
    plt.axhline(3.0, color="green", linestyle="--", label="Threshold (3 m/s²)")
    plt.title("Average Acceleration and Airborne Periods")
    plt.xlabel("Time (s)")
    plt.ylabel("Acceleration (m/s²)")
    plt.legend()
    plt.grid()


    plt.tight_layout()
    pdf.savefig()
    plt.close()

print(f"Visualization saved as {output_pdf}")
