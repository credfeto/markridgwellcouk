import webapp2
import utils
import commonactions

class TaskBufferHandler(webapp2.RequestHandler):

    def get(self):

        utils.add_response_headers(self.request, self.response.headers)
        self.response.headers['Content-Type'] = "text/plain"

        status = commonactions.publish_next()

        self.response.out.write(status + "\r\n")


app = webapp2.WSGIApplication([
    ('/tasks/buffer', TaskBufferHandler)
])
