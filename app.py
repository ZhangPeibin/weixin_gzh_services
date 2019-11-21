from flask import Flask, request
import request.gzh_info_request as gzh_info
app = Flask(__name__)


@app.route('/gzh/info/')
def request_gzh_info():
    args1 = request.args.get('name')
    print("args1=%s" % args1)
    gzh_list_data, gzh_page = gzh_info.request_gzh_list(args1)
    return gzh_list_data


if __name__ == '__main__':
    app.run()
