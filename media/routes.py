from flask import Blueprint, request, send_file
from .models import Media, Track
from song.models import Song

router = Blueprint("media", __name__)


@router.route("/media/<mtype>/<oid>")
def media(mtype, oid):
    if True:
        _file = Media.objects(pk=oid).first()
        if _file:
            return _file._file.read()
        else:
            return "<h1>404</h1>", 404
        return "Hey"
    else:
        return 'file'


@router.route("/test", methods=["GET", "POST"])
def pg():

    if request.method == "POST":

        try:
            body = request.form
            track = Track(title=body["title"], genre=body["genre"])
            print(track)
            return "Hold up"
        except Exception as e:
            print(e)

    else:
        try:
            IP = request.remote_addr
            print(request.referrer)
            img = Media.objects().first()
            # return  send_file(img._file, download_name="file.png")
            return {"IP": str(IP)}

        except Exception as e:
            print(e)
            return "Something went wrong", 500


r = [
    "__annotations__",
    "__class__",
    "__delattr__",
    "__dict__",
    "__dir__",
    "__doc__",
    "__enter__",
    "__eq__",
    "__exit__",
    "__format__",
    "__ge__",
    "__getattribute__",
    "__gt__",
    "__hash__",
    "__init__",
    "__init_subclass__",
    "__le__",
    "__lt__",
    "__module__",
    "__ne__",
    "__new__",
    "__reduce__",
    "__reduce_ex__",
    "__repr__",
    "__setattr__",
    "__sizeof__",
    "__str__",
    "__subclasshook__",
    "__weakref__",
    "_cached_json",
    "_get_file_stream",
    "_get_stream_for_parsing",
    "_load_form_data",
    "_parse_content_type",
    "accept_charsets",
    "accept_encodings",
    "accept_languages",
    "accept_mimetypes",
    "access_control_request_headers",
    "access_control_request_method",
    "access_route",
    "application",
    "host_url",
    "if_match",
    "if_modified_since",
    "if_none_match",
    "if_range",
    "if_unmodified_since",
    "input_stream",
    "is_json",
    "is_multiprocess",
    "is_multithread",
    "is_run_once",
    "is_secure",
    "json",
    "json_module",
    "list_storage_class",
    "make_form_data_parser",
    "max_content_length",
    "max_form_memory_size",
    "max_forwards",
    "method",
    "mimetype",
    "mimetype_params",
    "on_json_loading_failed",
    "origin",
    "parameter_storage_class",
    "path",
    "pragma",
    "query_string",
    "range",
    "referrer",
    "remote_addr",
    "remote_user",
    "root_path",
    "root_url",
    "routing_exception",
    "scheme",
    "script_root",
    "server",
    "shallow",
    "stream",
    "trusted_hosts",
    "url",
    "url_charset",
    "url_root",
    "url_rule",
    "user_agent",
    "user_agent_class",
    "values",
    "view_args",
    "want_form_data_parsed",
]
