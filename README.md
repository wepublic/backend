# Wepublic Backend

## Dev Setup

Instruction for Ubuntu 16.04, Adapt them to your OS

1. install python3, pip3 and virtualenv on your machine
2. Create a new Directory for the backend source and the virtualenv: `$ cd /somewhere/you/like/ && mkdir wp_backend && cd wp_backend`
3. create a new python virtualenv with python3 as your interpreter of choice: ` $ virtualenv -p python3 ./venv`
4. Activate the virtualenv: `$ source ./venv/bin/activate`
5. clone repo from git: `$ git clone git@github.com:wepublic/backend.git`
6. move into repo and install dependencies: `$ cd backend && pip install -r requirements.txt`
7. migrate your local db: `$ python manage.py migrate`
8. create admin user: `$ python manage.py createsuperuser`
9. run the App: `$ python manage.py runserver`


## API
Folgend API-Endpoints stehen zur verfügung:

* `/Users/`
* `/Tags/`
* `/Questions/`
* `/Answers/` 
* `/News/`

Die Authentifizierung erfolgt mit Tokens. Bei der Registrierung neuer User wird ein Token angelegt und zurückgegeben. Dieser sollte unter allen umständen geheim 
gehalten werden. Bei vielen Anfragen ist es notwendig, den Token zur Authentifizierung mitzuschicken. Das erfolg über den HTTP Head Authorization:
```
Authorization: Token <Geheimer Token>
```
Wichtig ist hierbei, das Leerzeichen zwischen dem Keyword `Token` und dem eigentlich Access Token zu beachten. 
Soweit nicht anders angegeben, sollte der Token immer mitgeschickt werden. 


Rückgabe der API ist immer JSON. 

### Domain Model

Die API Arbeitet mit folgenden Objekten

```
User:
{
  "id": 4,  # Integer Value, READ_ONLY
  "email": "juergen@test.de", # String, not_required
  "username": "jürgen",  # String, required, 
  "first_name": "", # String, not_required,
  "last_name": "", # String, not_required
  "reputation": 124, # Integer Value, READ_ONLY
  "profile_pic": "example.com/media/pic.png", # String Value, not Req
  "zip_code": "", # String value, not_required
  "year_of_birth": null, # Integer Value, not_required
  "gender": "", #String Value, not_required
  "password": "SecretSecret" # String, WRITE_ONLY
}

Question:


{
  "id": 50, # Integer, READ_ONLY
  "upvotes": 2, # Integer, READ_ONLY
  "voted": true, # Boolean, READ_ONLY
  "answers": [ # List, READ_ONLY
      {
          "id": 31,  # Int, Answer ID
          "user": 16 # Int User ID
      },
      ...
  ],
  "user": { # Object, READ_ONLY
      "url": "http://example.com/Users/16/",
      "id": 16,
      "username": "domenicoreising",
      "profile_pic": null
  },
  "text": "QuestionText", # String, required
  "time_created": "2017-06-27T14:33:39.189911Z", # TimeStamp, READ_ONLY
  "last_modified": "2017-06-27T14:33:39.300687Z",# TimeStamp, READ_ONLY
  "tags": [ # List of INTS
      7,
      38,
      20,
      17
  ]
}

Answer:

{
    "id": 1,
    "user": {
        "url": "http://localhost:8000/Users/2/",
        "id": 2,
        "username": "rudikobelt",
        "profile_pic": null
    },
    "question": {
        "url": "http://localhost:8000/Questions/27/",
        "text": "Make (install from source) python without running tests",
        "id": 27
    },
    "upvotes": 3,
    "voted": true,
    "text": "bla Bla",
    "time_created": "2017-06-27T14:33:39.327567Z",
    "last_modified": "2017-07-12T12:20:48.449430Z"
}

Tag:
{
    "id": 1, # READ_ONLY
    "text": "Gentechnik"
},

```

### `/Users/`

Dieser Endpoint stellt funktionen zum allgemeinen Usermanagement bereit. Folgende actions sind Verfügbar:

#### `/Users/`
 
#### GET:
    Wenn der Nutzer der Gruppe "Staff" angehört, werden alle nutzer über diesen Endpoint ausgegeben.
```HTTP
GET /Users/ HTTP/1.1
Host: localhost:8000
Authorization: Token f6e89846a2bc150beed57f6e4c12e0159dc59d17
Content-Type: application/json

RETURNS:
[
    {
        "id": 1,
        "email": "mattu@test.de",
        "username": "mattu",
        "first_name": "",
        "last_name": "",
        "reputation": 0,
        "profile_pic": null,
        "zip_code": "",
        "year_of_birth": null,
        "gender": ""
    },
...
]
```
#### POST: 
    Neue Nutzer können hier angelegt werden. Als json wird dann das user object geschickt.
    Benötigte felder sind:
    ```
    email
    password
    username
    Optional sind:
    first_name
    last_name
    profile_pic
    year_of_birth
    zip_code
    gender
    ```
```HTTP
POST /Users/ HTTP/1.1
Host: localhost:8000
Content-Type: application/json
{
	"email": "email@test.de",
	"password": "test1234",
	"username": "user",
	"zip_code": "143",
	"first_name": "Jana"
}

RETURNS:
{
    "id": 22,
    "email": "email@test.de",
    "username": "user",
    "first_name": "Jana",
    "last_name": "",
    "reputation": 0,
    "profile_pic": null,
    "zip_code": "143",
    "year_of_birth": null,
    "gender": "",
    "token": "cd873294d63a7e34eea5bff87244a6700d804d8b"
}
```

### `/Users/{pk}`
#### GET:
    Wenn pk = id vom nutzer, dann wird dessen user objekt zurückgegeben, ansonsten fehlermeldung wegen not authorized. 
    Wenn user dem Staff angehört können alle user nachgeschlagen werden.

```HTTP
GET /Users/21/ HTTP/1.1
Host: localhost:8000
Authorization: Token f6e89846a2bc150beed57f6e4c12e0159dc59d17
Content-Type: application/json

RETURNS:

{
    "id": 21,
    "email": "marietta.becker@gmail.com",
    "username": "mariettabecker",
    "first_name": "Marietta",
    "last_name": "Becker",
    "reputation": 0,
    "profile_pic": null,
    "zip_code": "606",
    "year_of_birth": 2011,
    "gender": "M"
}
```


#### PATCH:
    User Informationen können so geupdated werden. Die Felder im User object die sich ändern sollten als JSON übergeben werden ( Nur staff oder den eigenen )

```HTTP
PATCH /Users/21/ HTTP/1.1
Host: localhost:8000
Authorization: Token f6e89846a2bc150beed57f6e4c12e0159dc59d17
Content-Type: application/json
{
	"first_name": "Hubert",
	"gender": "W"
}

RETURNS:
{
    "id": 21,
    "email": "marietta.becker@gmail.com",
    "username": "mariettabecker",
    "first_name": "Hubert",
    "last_name": "Becker",
    "reputation": 0,
    "profile_pic": null,
    "zip_code": "606",
    "year_of_birth": 2011,
    "gender": "W"
}

```

#### DELETE:
    Löscht den User aus der Datenbank ( Nur Staff oder den eigenen )

```HTTP
DELETE /Users/22/ HTTP/1.1
Host: localhost:8000
Authorization: Token f6e89846a2bc150beed57f6e4c12e0159dc59d17
Content-Type: application/json

RETURNS:
{
    "status": "ok"
}

```

### `/Users/me/`
####GET:
    Shortcut wenn man schnell mal an sein User Objekt kommen möchte

```HTTP
GET /Users/me HTTP/1.1
Host: localhost:8000
Authorization: Token f6e89846a2bc150beed57f6e4c12e0159dc59d17
Content-Type: application/json

RETURNS:
{
    "id": 1,
    "email": "mattu@test.de",
    "username": "mattu",
    "first_name": "",
    "last_name": "",
    "reputation": 0,
    "profile_pic": null,
    "zip_code": "",
    "year_of_birth": null,
    "gender": ""
}
```
    
### `/Users/token/`
#### POST:
    Gibt den token zurück wenn ein json object mit den feldern email und password und den richtigen werten geschickt wird
    Hier muss kein Token mitgeschickt werden.

```HTTP
POST /Users/token/ HTTP/1.1
Host: localhost:8000
Content-Type: application/json
{
	"email": "bernfried.gertz@yahoo.de",
	"password": "password"
}

RETURNS:
{
    "Token": "0c5e8275860b1df6f299c5c27f9bf55c4e9ec895"
}
```

### `/Users/logout/`
#### GET:
    Löscht den token aus der Datenbank. ein Neuer muss anschließend über /Users/Token generiert werden.

```HTTP
GET /Users/logout/ HTTP/1.1
Host: localhost:8000
Content-Type: application/json
Authorization: Token 0c5e8275860b1df6f299c5c27f9bf55c4e9ec895

RETURNS:
{
    "status": "logged out"
}
```

### `/Users/change_password/`
#### POST:
    Ändert das Password und generiert einen neuen Token.
```HTTP
POST /Users/change_password/ HTTP/1.1
Host: localhost:8000
Content-Type: application/json
{
	"email": "bernfried.gertz@yahoo.de",
	"password": "password",
	"new_password": "test1234"
}

RETURNS:
{
    "Token": "9771015794b2eb48af9e683db645303e561f4333"
}
```
### `/Tags/`
Stellt informationen über tags bereit. Staff nutzer können neue Anlegen oder welche verändern

#### `/Tags/`
#### GET:
    Gibt eine List aller tags zurück
```HTTP
GET /Tags/ HTTP/1.1
Host: localhost:8000
Content-Type: application/json

RETURNS:
[
    {
        "id": 1,
        "text": "TAG1"
    },
    {
        "id": 2,
        "text": "TAG2"
    },
...
]
```

#### POST:
legt einen neuen Tag an, Wenn man staff User ist.

```HTTP
POST /Tags/ HTTP/1.1
Host: localhost:8000
Authorization: Token f6e89846a2bc150beed57f6e4c12e0159dc59d17
Content-Type: application/json
{
  "text": "Neuer Supertag"
}

RETURNS:
{
    "id": 41,
    "text": "Neuer Supertag"
}
```

#### `/Tags/{pk}/Questions/`
#### GET:
Gibt eine liste Aller Question die mit dem Tag mit der id pk getaggt sind zurück

```HTTP
GET /Tags/1/Questions/ HTTP/1.1
Host: localhost:8000
Authorization: Token f6e89846a2bc150beed57f6e4c12e0159dc59d17
Content-Type: application/json
```

returns:
```JSON
[
    {
        "id": 28,
        "voted": false,
        "answers": [
            {
                "id": 21,
                "user": 13
            },
            {
                "id": 37,
                "user": 6
            },
            {
                "id": 46,
                "user": 10
            }
        ],
        "user": {
            "url": "http://localhost:8000/Users/14/",
            "id": 14,
            "username": "ottokartrub",
            "profile_pic": null
        },
        "text": "How to improve load time of zsh in babun on windows?",
        "time_created": "2017-06-27T14:33:37.793874Z",
        "last_modified": "2017-06-27T14:33:37.844040Z",
        "tags": [
            9,
            2,
            40,
            1
        ]
    },
]
```

### `/Questions/`
Stellt question management bereit

#### `/Questions/`
#### GET:
Gibt eine List der neuesten Fragen zurück.
Die Pagination beschränkt die Ergebnisse pro anfrage auf 20. Sollen die nächsten 20 ergebnisse geladen werden, muss ?page=n angehängt werden. Links zur nächsten und vorigen seiten werden mitgeschickt. 
Die List kann anhand des Erstelldatums sowie der Anzahl der Upvotes sortiert werden. Hierfür muss folendes an die GET-URL angehängt werden:
```
?ordering=-time_created : Absteigend nach Erstelldatum ( Neueste zuerst ) 
?ordering=time_created : Aufsteigend nach Erstelldatum ( Älteste zuerst ) 
?ordering=-upvotes : Absteigend nach Upvotes ( Meisten Votes zuerst )
?ordering=upvotes : Aufsteigend nach Upvotes ( wenigste Votes zuerst )
```

```HTTP
GET /Questions/?ordering=-upvotes HTTP/1.1
Host: localhost:8000
Authorization: Token f6e89846a2bc150beed57f6e4c12e0159dc59d17
Content-Type: application/json

RETURNS:
{
    "count": 50,
    "next": "http://localhost:8000/Questions/?ordering=-upvotes&page=2",
    "previous": null,
    "results": [
        {
            "id": 21,
            "upvotes": 8,
            "voted": true,
            "answers": [
                {
                    "id": 24,
                    "user": 4
                },
                {
                    "id": 33,
                    "user": 6
                },
                {
                    "id": 61,
                    "user": 18
                },
                {
                    "id": 68,
                    "user": 18
                }
            ],
            "user": {
                "url": "http://localhost:8000/Users/10/",
                "id": 10,
                "username": "h-dieternerger",
                "profile_pic": null
            },
            "text": "Get session id in tomcat access logs for angular js application",
            "time_created": "2017-06-27T14:33:37.379889Z",
            "last_modified": "2017-06-27T14:33:37.388886Z",
            "tags": []
        },
]
```

#### POST:
erstellt eine neue Frage. Fragetext und Tags müssen übergeben werden:

```HTTP
POST /Questions/ HTTP/1.1
Host: localhost:8000
Authorization: Token f6e89846a2bc150beed57f6e4c12e0159dc59d17
Content-Type: application/json
{
	"text": "Blablabla blablabla?",
	"tags": [1,	4, 5]
}

RETURNS:
{
    "id": 51,
    "voted": false,
    "answers": [],
    "user": {
        "url": "http://localhost:8000/Users/1/",
        "id": 1,
        "username": "mattu",
        "profile_pic": null
    },
    "text": "Blablabla blablabla?",
    "time_created": "2017-07-12T14:08:39.409012Z",
    "last_modified": "2017-07-12T14:08:39.409046Z",
    "tags": [
        1,
        4,
        5
    ]
}
```

#### `/Questions/{pk}/`
##### GET:
Gibt die Frage mit der id {pk} zurück

```
GET /Questions/51/ HTTP/1.1
Host: localhost:8000
Content-Type: application/json

RETURNS:
{
    "id": 51,
    "upvotes": null,
    "voted": false,
    "answers": [],
    "user": {
        "url": "http://localhost:8000/Users/1/",
        "id": 1,
        "username": "mattu",
        "profile_pic": null
    },
    "text": "Blablabla blablabla?",
    "time_created": "2017-07-12T14:08:39.409012Z",
    "last_modified": "2017-07-12T14:08:39.409046Z",
    "tags": [
        1,
        4,
        5
    ]
}
```

##### PATCH:
Erlaubt es, einzelne oder Alle felder einer Frage zu bearbeiten. Erwartet ein JSON objekt. Nur, wenn man selber der Ersteller der Frage oder Staff ist.

```HTTP
PATCH /Questions/51/ HTTP/1.1
Host: localhost:8000
Authorization: Token f6e89846a2bc150beed57f6e4c12e0159dc59d17
Content-Type: application/json
{
	"tags": [1, 4, 5, 12]
}

RETURNS:
{
    "id": 51,
    "upvotes": null,
    "voted": false,
    "answers": [],
    "user": {
        "url": "http://localhost:8000/Users/1/",
        "id": 1,
        "username": "mattu",
        "profile_pic": null
    },
    "text": "Blablabla blablabla?",
    "time_created": "2017-07-12T14:08:39.409012Z",
    "last_modified": "2017-07-12T14:12:28.183864Z",
    "tags": [
        1,
        4,
        5,
        12
    ]
}
```
##### DELETE:
Löscht eine Frage. Nur, wenn man selber der Ersteller der Frage oder Staff ist.
```HTTP
DELETE /Questions/51/ HTTP/1.1
Host: localhost:8000
Authorization: Token f6e89846a2bc150beed57f6e4c12e0159dc59d17
Content-Type: application/json

RETURNS:
<NOTHING>
```
#### `/Questions/{pk}/tags/`
##### GET:
Gibt die Liste der Tags der Frage mit der id {pk} zurück. inklusive Text der tags:

```HTTP
GET /Questions/47/tags/ HTTP/1.1
Host: localhost:8000
Authorization: Token f6e89846a2bc150beed57f6e4c12e0159dc59d17
Content-Type: application/json

RETURNS:
[
    {
        "id": 6,
        "text": "dippel"
    },
    {
        "id": 23,
        "text": "lange"
    }
]
```

#### `/Questions/{pk}/upvote/`
##### POST:
Gibt der Frage mit der ID {pk} einen Daumen Hoch. Post data kann leer sein.
```HTTP
POST /Questions/47/upvote/ HTTP/1.1
Host: localhost:8000
Authorization: Token f6e89846a2bc150beed57f6e4c12e0159dc59d17
Content-Type: application/json

RETURNS:
{
    "id": 47,
    "upvotes": 1,
    "voted": true,
    "answers": [],
    "user": {
        "url": "http://localhost:8000/Users/15/",
        "id": 15,
        "username": "pierrestoll",
        "profile_pic": null
    },
    "text": "Cross Origin in ajax not working for .properties file in IOS (10.3.1)",
    "time_created": "2017-06-27T14:33:39.033336Z",
    "last_modified": "2017-06-27T14:33:39.078098Z",
    "tags": [
        6,
        23
    ]
}
```
#### `/Questions/{pk}/downvote/`
#####POST:
Gibt der Frage mit der ID {pk} einen Daumen runter. Post data kann leer sein.
```HTTP 
POST /Questions/47/downvote/ HTTP/1.1
Host: localhost:8000
Authorization: Token f6e89846a2bc150beed57f6e4c12e0159dc59d17
Content-Type: application/json

RETURNS:
{
    "id": 47,
    "upvotes": null,
    "voted": true,
    "answers": [],
    "user": {
        "url": "http://localhost:8000/Users/15/",
        "id": 15,
        "username": "pierrestoll",
        "profile_pic": null
    },
    "text": "Cross Origin in ajax not working for .properties file in IOS (10.3.1)",
    "time_created": "2017-06-27T14:33:39.033336Z",
    "last_modified": "2017-06-27T14:33:39.078098Z",
    "tags": [
        6,
        23
    ]
}
```
#### `/Questions/upvotes/`
#####GET:
Gibt eine Liste der Fragen der man Daumen Hoch gegeben hat zurück
```
GET /Questions/upvotes/ HTTP/1.1
Host: localhost:8000
Authorization: Token f6e89846a2bc150beed57f6e4c12e0159dc59d17
Content-Type: application/json

RETURNS:
[
    {
        "id": 49,
        "upvotes": 3,
        "voted": true,
        "answers": [
            {
                "id": 5,
                "user": 19
            },
            {
                "id": 72,
                "user": 1
            }
        ],
        "user": {
            "url": "http://localhost:8000/Users/1/",
            "id": 1,
            "username": "mattu",
            "profile_pic": null
        },
        "text": "Late linking to existing elf with GCC/LD",
        "time_created": "2017-06-27T14:33:39.140445Z",
        "last_modified": "2017-06-27T14:33:39.166331Z",
        "tags": []
    },
]
```
#### `/Questions/downvotes/`
##### GET:
Gibt eine Liste der Fragen der man Daumen runter gegeben hat zurück
```HTTP
GET /Questions/downvotes/ HTTP/1.1
Host: localhost:8000
Authorization: Token f6e89846a2bc150beed57f6e4c12e0159dc59d17
Content-Type: application/json

RETURNS:
[
    {
        "id": 8,
        "upvotes": 5,
        "voted": true,
        "answers": [],
        "user": {
            "url": "http://localhost:8000/Users/9/",
            "id": 9,
            "username": "bernfriedgertz",
            "profile_pic": null
        },
        "text": "Template parse errors when overriding DataTable component of primeNg",
        "time_created": "2017-06-27T14:33:36.567457Z",
        "last_modified": "2017-06-27T14:33:36.611340Z",
        "tags": [
            33,
            20
        ]
    },
]
```

#### `/Questions/my/`
#### GET:
Gibt alle fragen zurück, die man selbst erstellt hat
```HTTP
GET /Questions/my HTTP/1.1
Host: localhost:8000
Authorization: Token f6e89846a2bc150beed57f6e4c12e0159dc59d17
Content-Type: application/json

RETURNS:
[
    {
        "id": 5,
        "upvotes": 5,
        "voted": false,
        "answers": [
            {
                "id": 17,
                "user": 7
            },
            {
                "id": 53,
                "user": 7
            },
            {
                "id": 62,
                "user": 16
            }
        ],
        "user": {
            "url": "http://localhost:8000/Users/1/",
            "id": 1,
            "username": "mattu",
            "profile_pic": null
        },
        "text": "Error in hadoop jobs due to hive query error",
        "time_created": "2017-06-27T14:33:36.453012Z",
        "last_modified": "2017-06-27T14:33:36.463165Z",
        "tags": []
    },
]
```

## `/Answers/`


