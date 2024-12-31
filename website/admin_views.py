from flask_admin import AdminIndexView, expose
from flask_basicauth import BasicAuth

class MyAdminIndexView(AdminIndexView):
    def __init__(self, basic_auth, *args, **kwargs):
        super(MyAdminIndexView, self).__init__(*args, **kwargs)
        self.basic_auth = basic_auth

    @expose('/')
    def index(self):
        if not self.basic_auth.authenticate():
            return self.basic_auth.challenge()
        return super(MyAdminIndexView, self).index()
