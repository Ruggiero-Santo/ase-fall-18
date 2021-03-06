from flakon import JsonBlueprint
from flask import request, jsonify, abort
from myservice.classes.poll import Poll, NonExistingOptionException, UserAlreadyVotedException

doodles = JsonBlueprint('doodles', __name__)

_ACTIVEPOLLS = {} # list of created polls
_POLLNUMBER = 0 # index of the last created poll

@doodles.route("/doodles", methods = ["GET", "POST"]) # complete the decoration
def all_polls():

    if request.method == 'POST':
        result = create_doodle(request.get_json())
    elif request.method == 'GET':
        result = get_all_doodles()

    return result

@doodles.route("/doodles/<int:id>", methods = ["GET", "DELETE", "PUT"]) # complete the decoration
def single_poll(id):
    global _ACTIVEPOLLS
    result = ""

    exist_poll(id) # check if the Doodle is an existing one
    if request.method == 'GET': #retrieve a poll
        result = jsonify(_ACTIVEPOLLS[id].serialize())
    elif request.method == 'DELETE': # delete a poll and get back winners
        result = jsonify(winners = _ACTIVEPOLLS[id].get_winners())
        del _ACTIVEPOLLS[id]
    elif request.method == 'PUT': #vote in a poll
        result = jsonify(winners = vote(id, request.get_json()))

    return result

@doodles.route("/doodles/<int:id>/<person>", methods = ["GET", "DELETE"]) #complete the decoration
def person_poll(id, person):
    global _ACTIVEPOLLS

    exist_poll(id)# check if the Doodle exists
    poll = _ACTIVEPOLLS[id]
    if request.method == 'GET':# retrieve all preferences cast from <person> in poll <id>
        result = jsonify(votedoptions = poll.get_voted_options(person))
    elif request.method == 'DELETE': #delete all preferences cast from <person> in poll <id>
        result = jsonify(removed = poll.delete_voted_options(person))

    return result

def vote(id, data):
    global _ACTIVEPOLLS

    try:
        return _ACTIVEPOLLS[id].vote(data["person"], data["option"])
    except UserAlreadyVotedException:
        abort(400) # Bad Request
    except NonExistingOptionException:
        abort(400) # manage the NonExistingOptionException

def create_doodle(data):
    global _ACTIVEPOLLS, _POLLNUMBER
    #create a new poll in _ACTIVEPOLLS based on the input JSON. Update _POLLNUMBER by incrementing it.
    _POLLNUMBER += 1
    _ACTIVEPOLLS.update({_POLLNUMBER:  Poll(_POLLNUMBER, data["title"], data["options"])})
    return jsonify(pollnumber = _POLLNUMBER)

def get_all_doodles():
    global _ACTIVEPOLLS
    return jsonify(activepolls = [e.serialize() for e in _ACTIVEPOLLS.values()])

def exist_poll(id):
    global _ACTIVEPOLLS, _POLLNUMBER

    if int(id) > _POLLNUMBER:
        abort(404) # error 404: Not Found, i.e. wrong URL, resource does not exist
    elif not(id in _ACTIVEPOLLS):
        abort(410) # error 410: Gone, i.e. it existed but it's not there anymore
