import pandas as pd
import json

# Define the data as a list of lists
# data = [
#     [0,3.15,9.23,-0.16,-0.52,-0.63,-0.32,-0.48,1.73,9.41,0.75,-0.60,-0.59,-0.32,-0.44,-2.96,8.39,4.26,0.47,0.41,-0.35,-0.70],
#     [14,3.18,9.21,-0.16,-0.52,-0.63,-0.32,-0.48,1.82,9.42,0.71,-0.60,-0.59,-0.32,-0.44,-3.01,8.37,4.31,0.47,0.41,-0.35,-0.70],
#     [27,3.25,9.20,-0.20,-0.52,-0.63,-0.32,-0.48,1.77,9.43,0.69,-0.60,-0.59,-0.32,-0.44,-2.96,8.36,4.37,0.47,0.41,-0.35,-0.70],
#     [39,2.99,9.31,-0.14,-0.52,-0.63,-0.32,-0.48,1.68,9.44,0.71,-0.60,-0.59,-0.32,-0.44,-2.73,8.48,4.29,0.47,0.41,-0.35,-0.70],
#     [50,2.90,9.32,-0.09,-0.52,-0.63,-0.32,-0.48,1.47,9.50,0.77,-0.60,-0.59,-0.32,-0.44,-2.61,8.52,4.30,0.47,0.41,-0.35,-0.70],
#     [64,2.80,9.35,-0.06,-0.52,-0.63,-0.32,-0.48,1.29,9.45,0.86,-0.60,-0.59,-0.32,-0.44,-2.45,8.55,4.12,0.47,0.41,-0.35,-0.70],
#     [78,2.71,9.32,-0.02,-0.52,-0.63,-0.32,-0.48,1.16,9.44,0.88,-0.60,-0.59,-0.32,-0.44,-2.29,8.54,4.17,0.47,0.41,-0.35,-0.70]
# ]

# Read the CSV file into a DataFrame
data = pd.read_csv("dummy_data.csv")

# Create a DataFrame
# df = pd.DataFrame(data, columns=columns)

# Specify the column indices to delete (e.g., columns 8 through 14)
columns_to_delete = list(range(8, 15))

# Drop the specified columns
df = data.drop(columns=data.columns[columns_to_delete])

# Export the modified DataFrame to a CSV file
df.to_csv("cleaned_data.csv", index=False)

output_data = {
    "device_name": "DUMMY_DEVICE_123",
    "timestamps": df.iloc[:, 0].tolist(),
    "Ax1": df.iloc[:, 1].tolist(),
    "Ay1": df.iloc[:, 2].tolist(),
    "Az1": df.iloc[:, 3].tolist(),
    "Ox1": df.iloc[:, 4].tolist(),
    "Oy1": df.iloc[:, 5].tolist(),
    "Oz1": df.iloc[:, 6].tolist(),
    "Ow1": df.iloc[:, 7].tolist(),
    "Ax2": df.iloc[:, 8].tolist(),
    "Ay2": df.iloc[:, 9].tolist(),
    "Az2": df.iloc[:, 10].tolist(),
    "Ox2": df.iloc[:, 11].tolist(),
    "Oy2": df.iloc[:, 12].tolist(),
    "Oz2": df.iloc[:, 13].tolist(),
    "Ow2": df.iloc[:, 14].tolist(),
}

# Save the structured data to a JSON file
with open("cleaned_data.json", "w") as json_file:
    json.dump(output_data, json_file, indent=4)

print("Data converted and saved as 'output.json'.")

print("Columns deleted and CSV file saved as 'output.csv'.")
print("Shape of the DataFrame:", df.shape)
