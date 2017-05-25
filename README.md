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
* `/Answers/` --> Noch nicht fertig

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
  "username": "jürgen",  # String, required, 
  "first_name": "", # String, not_required,
  "last_name": "", # String, not_required
  "email": "juergen@test.de", # String, not_required
  "reputation": 124, # Integer Value, READ_ONLY
  "password": "SecretSecret" # String, WRITE_ONLY
}
Question:
{
  "id": 4, # Integer, READ_ONLY
  "upvotes": 1, # READ_ONLY
  "downvotes": 0, # READ_ONLY
  "creator": { # READ_ONLY
    "id": 2,
    "username": "roland"
  },
  "text": "Was werden sie als BundekanzlerIn dafür unternehmen, dass die Energiewende für die privaten Haushalte bezahlbar bleibt?",
  "time_created": "2017-05-18T18:19:00.906169Z", #READ_ONLY
  "last_modified": "2017-05-18T18:19:00.906214Z", #READ_ONLY
  "tags": [ # list of INTs
    4
  ]
}

{
    "id": 1, # READ_ONLY
    "text": "Gentechnik"
},


```

### `/Users/`

Dieser Endpoint stellt funktionen zum allgemeinen Usermanagement bereit. Folgende actions sind Verfügbar:

#### `/Users/
 
- GET:
    Wenn der Nutzer der Gruppe "Staff" angehört, werden alle nutzer über diesen Endpoint ausgegeben.
- POST: 
    Neue Nutzer können hier angelegt werden. Als json wird dann das user object geschickt.
    Benötigte felder sind:
    ```
    username
    password
    email
    Optional sind:
    first_name
    last_name
    ```

### `/Users/{pk}`
- GET:
    Wenn pk = id vom nutzer, dann wird dessen user objekt zurückgegeben, ansonsten fehlermeldung wegen not authorized. 
    Wenn user dem Staff angehört können alle user nachgeschlagen werden.
- PATCH:
    User Informationen können so geupdated werden. Die Felder im User object die sich ändern sollten als JSON übergeben werden ( Nur staff oder den eigenen )
- DELETE:
    Löscht den User aus der Datenbank ( Nur Staff oder den eigenen )

### `/Users/me/`
- GET:
    Shortcut wenn man schnell mal an sein User Objekt kommen möchte
    
### `/Users/token/`
- POST:
    Gibt den token zurück wenn ein json object mit den feldern username und password und den richtigen werten geschickt wird
    Hier muss kein Token mitgeschickt werden.
### `/Users/logout/`
- GET:
    Löscht den token aus der Datenbank. ein Neuer muss anschließend über /Users/Token generiert werden.


### `/Tags/`
Stellt informationen über tags bereit. Staff nutzer können neue Anlegen oder welche verändern

#### `/Tags/`
- GET:
    Gibt eine List aller tags zurück
- POST:
    legt einen neuen Tag an

#### `/Tags/{pk}/Questions/`
- GET:
    Gibt eine liste Aller Question die mit dem Tag mit der id pk getaggt sind zurück

### `/Questions/`
Stellt rudimentäres question management bereit

#### `/Questions/`
- GET:
    Gibt eine List der neuesten Fragen zurück. Das ergebnis hat folgendes Format:
    ```
    {
      "count": 123,
      "next": "http://example.com/Questions/?page=3",
      "previous": "http://example.com/Questions/?page=1",
      "results": [
        {
          "id": 4,
          "upvotes": 1,
          "downvotes": 0,
          "creator": {
            "id": 2,
            "username": "roland"
          },
          "text": "Was werden sie als BundekanzlerIn dafür unternehmen, dass die Energiewende für die privaten Haushalte bezahlbar bleibt?",
          "time_created": "2017-05-18T18:19:00.906169Z",
          "last_modified": "2017-05-18T18:19:00.906214Z",
          "tags": [
            4
          ]
        },
            .... Andere Fragen
      ]
    }
    ```

    Die Pagination beschränkt die Ergebnisse pro anfrage auf 50. Sollen die nächsten 50 ergebnisse geladen werden, muss ?page=n angehängt werden. Links zur nächsten und vorigen seiten
    werden mitgeschickt. 
- POST:
    erstellt eine neue Frage. Akzeptiert folgendes Objekt:
    ```
    {
        "text": "Fragetext"
        "tags": [
            1, # id der Tags
            2,
            52
        ]
    }
    ```

#### `/Questions/{pk}/`
- GET:
    Gibt die Frage mit der id {pk} zurück
- PATCH:
    Erlaubt es, einzelne oder Alle felder einer Frage zu bearbeiten. Erwartet ein JSON objekt. Nur, wenn man selber der Ersteller der Frage oder Staff ist.
- DELETE:
    Löscht eine Frage. Nur, wenn man selber der Ersteller der Frage oder Staff ist.

#### `/Questions/{pk}/tags/
- GET:
    Gibt die Liste der Tags der Frage mit der id {pk} zurück. inklusive Text der tags:
    ```
    [
      {
        "id": 4,
        "text": "Energiewende"
      },
      ... andere Tags
    ]
    ```

#### `/Questions/{pk}/upvote/`
- POST:
    Gibt der Frage mit der ID {pk} einen Daumen Hoch. Post data kann leer sein.
    
#### `/Questions/{pk}/downvote/`
- POST:
    Gibt der Frage mit der ID {pk} einen Daumen runter. Post data kann leer sein.

#### `/Questions/upvotes/`
- GET:
    Gibt eine Liste der Fragen der man Daumen Hoch gegeben hat zurück

#### `/Questions/downvotes/`
- GET:
    Gibt eine Liste der Fragen der man Daumen runter gegeben hat zurück

#### `/Questions/my/`
- GET:
    Gibt alle fragen zurück, die man selbst erstellt hat

