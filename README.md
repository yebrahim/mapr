# mapr
Sample web app for CSSI class at Google

This is a simple web app using App Engine in Python that authenticates users using the Google API,
and the user can put their birthplace on a map, which is stored in the backend using Datastore.
Another page with all the places on the map can be seen as well.

This is a good introduction to Datastore, it models a `Birthplace` with the user's name and
coordinates, and uses simple APIs for `put`, `get`, and `fetch`.
