import requests, apitoken, time, difflib

class smashGG:
    def __init__(self, id=None, slug=None):
        self.api = apitoken.token()
        self.url = "https://api.smash.gg/gql/alpha"
        self.id = id
        try:
            self.slug = slug.replace("https://", "").replace("smash.gg/user/", "")
        except:
            print("using id")

        # defining queries
        self.q_playersets = """
                    query Sets($id:ID!) {
                        player(id:$id) {
                            id
                            gamerTag
                            user {
                                discriminator
                            }
                            sets(perPage: 500, page: 1) {
                                nodes {
                                    id
                                    displayScore
                                    event {
                                        id
                                        name
                                        videogame {
                                            name
                                        }
                                    }
                                }
                            }
                        }
                    }
                """
        self.q_set_entrants = """
                    query User($descrim: String!) {
                        user(slug: $descrim) {
                            player {
                                gamerTag
                                sets(perPage: 500, page: 1) {
                                    nodes {
                                        id
                                        displayScore
                                        event {
                                        videogame {
                                            name
                                        }
                                        }
                                        slots {
                                            id
                                            entrant {
                                                participants {
                                                    gamerTag
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },"""
        self.q_playersetsBySlug = """
                            query User($descrim: String!) {
                                user(slug: $descrim) {
                                    player {
                                        id
                                        gamerTag
                                        sets(perPage: 500, page: 1) {
                                            nodes {
                                                id
                                                displayScore
                                                event {
                                                    id
                                                    name
                                                    videogame{
                                                        name
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            },"""
        self.create_set_lists()  


    def create_set_lists(self):
        if self.id != None:
            req = requests.post(
                self.url, data = {
                    "query": self.q_playersets, "variables": f'{{"id": {self.id}}}'
                }, headers={'Authorization': f'Bearer {self.api}'}).json()
            print(req)
            self.all_sets = req["data"]["player"]["sets"]["nodes"]
            self.tag = req["data"]["player"]["gamerTag"]
            self.slug = req["data"]["player"]["user"]["discriminator"]
                # returns a list of dicts with some sort of structure like this{id, displayScore, event={id, name, tournament={id, name}}} (everything inside of the nodes part of the query)

        elif self.slug != None:
            req = requests.post(
                self.url, data = {
                    "query": self.q_playersetsBySlug, "variables": f'{{"descrim": "{self.slug}"}}'
                }, headers={'Authorization': f'Bearer {self.api}'}).json()
            print(req)
            self.all_sets = req["data"]["user"]["player"]["sets"]["nodes"]
            self.tag = req["data"]["user"]["player"]["gamerTag"]

        else:
            print("Slug or id must be present")
            return

        self.sets_minusdqs = []
        
        for i in self.all_sets:
            if i["displayScore"] != "DQ":
                self.sets_minusdqs.append(i)
        self.games = []
        for i in range(len(self.sets_minusdqs)):
            if not self.sets_minusdqs[i]["event"]["videogame"]["name"] in self.games:
                self.games.append(self.sets_minusdqs[i]["event"]["videogame"]["name"])
        if len(self.games) > 1:
            self.games.insert(0, "Both") 


    def get_set_entrants(self):
        self.set_entrants = [] # will get all the entrants in the list of the players sets

        req = requests.post(
            self.url,
            data={
                "query": self.q_set_entrants,
                "variables": f'{{"descrim": "{self.slug}"}}',
            },
            headers={
                'Authorization': f'Bearer {self.api}',
            }
        ).json()
        print(req)
        req = req['data']["user"]["player"]['sets']["nodes"]

        
        for i in req:
            _temp = []
            if i["displayScore"] == "DQ":
                pass
            else:
                for it in i["slots"]:
                    _temp.append([i["id"], it['entrant']["participants"][0]['gamerTag'], i["event"]["videogame"]["name"]])
                self.set_entrants.append(_temp)
        return self.set_entrants# arranged where x[?] returns a nested list containing the following information [["SetId", "Player1Tag", game], ["SetId", "Player2Tag", game]] 
    

    def create_head2heads(self, game):
        Sets = self.get_set_entrants()
        # orders things into a dict with the key of the players name, and the value of a list of ids
        self.head2head = {}
        if game == "Both":
            for i in Sets: # for every set in the list of sets
                if i[0][1] == self.tag:
                    if i[1][1] == self.tag:
                        print("Error with head2heads")
                        return
                    else:
                        if i[1][1] in self.head2head:
                            self.head2head[i[1][1]].append(i[1][0])
                        else:
                            self.head2head[i[1][1]] = [i[1][0]]
                else:
                    if i[0][1] in self.head2head:
                        self.head2head[i[0][1]].append(i[0][0])
                    else:
                        self.head2head[i[0][1]] = [i[1][0]]
        else:
            for i in Sets: # for every set in the list of sets
                if i[0][2] == game:
                    if i[0][1] == self.tag:
                        if i[1][1] == self.tag:
                            print("Error with head2heads")
                            return
                        else:
                            if i[1][1] in self.head2head:
                                self.head2head[i[1][1]].append(i[1][0])
                            else:
                                self.head2head[i[1][1]] = [i[1][0]]
                    else:
                        if i[0][1] in self.head2head:
                            self.head2head[i[0][1]].append(i[0][0])
                        else:
                            self.head2head[i[0][1]] = [i[1][0]]
        self.opponents = list(self.head2head.keys())

    def get_opponents(self, game="Both"):
        _ = ["All"]
        self.create_head2heads(game)
        for i in self.opponents:
            _.append(i)
        return _

    def h2hscores(self, playerTag="all", game="Both"): # needs to be a list of id's not a list of sets
        self.create_head2heads(game)
        self.scores = []
        _temp = []
        
        for i in self.head2head:
            _temp.append(i)

        if playerTag != "All":
            if playerTag in _temp:
                _temp2 = difflib.get_close_matches(playerTag, _temp, n=3)
                for i in self.head2head[_temp2[0]]:
                    for it in self.sets_minusdqs:
                        if it["id"] == int(i):
                            self.scores.append(it["displayScore"])
            else:
                return(f"This user has not played against {playerTag}")

        else:
            for a in self.head2head:
                for i in self.head2head[a]:
                    print(i)
                    for it in self.sets_minusdqs:
                        if it["id"] == int(i):
                            self.scores.append(it["displayScore"])
        return self.scores