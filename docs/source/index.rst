.. Upboat documentation master file, created by
   sphinx-quickstart on Mon Dec  5 18:19:05 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Upboat this Guide
=================

Adding Social Voting to Your Pyramid App
----------------------------------------
So you've been to Reddit, Digg, StackOverflow, and the billion other sites that use social voting, and you love the concept of your users rating the importance of your content completely for free.  This guide will go through the basic steps of implementing such a system, and also give you some working source code to see how I created one.  I'm not really calling this a "tutorial" per se, as I am not going to really go through anything step by step.  I am mostly going to give you the higher level details.  Then using the code I have provided, and the concepts I introduce, you should be able to go out into the big wide world and write your own.  This seems fitting, as social voting is a piece of functionality that is very closely connected to your data, so having you create some dummy app with social voting might not be the best use of your time.  Due to this, I would say that this guide is probably written for moderate/advanced Pyramid/SQLAlchemy users.  So let's start.

So first things first, I have created a very simple social voting implementation `here <https://github.com/jayd3e/Upboat>`_.  In order to test it out, run the follow commands:

.. code-block:: text

    jayd3e ~/Projects/Upboat $ python setup.py develop
    jayd3e ~/Projects/Upboat $ python demos/demo.py

You should see something like this get printed out:

.. code-block:: text

    serving on 0.0.0.0:5020 view at http://127.0.0.1:5020

You can then view the application by going to http://127.0.0.1:5020 as it mentions.  Basically this page just demonstrates that a single user can click on the up/down vote arrows, and have those actions persisted in the database.  The demo really doesn't show much, as it only uses a single global user id, but if you were to actually implement this on a working site, with multiple users, each up/down vote would be linked to their respective user.  So anyway, how does it work?


Database Representation Of the Data
-----------------------------------
Let's start with the obvious things.  In order for something to get voted on, you need the "voted" and the "voter."    In other words, you need an object of some sort, usually a comment, post, or link, and a user to say they either like or dislike that object.  So using this knowledge we can create a primitive voting system(represented below in database tables):

**users**

=====  =====
id     name
=====  =====
1      steve
2      john
=====  =====

**posts**

===== ======== ===== ======= =======
id    title    body  owner   score
===== ======== ===== ======= =======
1     post1    text  wayne   3
2     post2    text  doug    -4
===== ======== ===== ======= =======

So here we have a pretty normal situation, you have a bunch of user created posts, that contain a title, text body, and an owner.  We could easily allow these posts to be voted upon by adding an up/down vote arrow next to each post in user interface, and then have a view that receives the id of the post and whether it was upvoted or downvoted.  This view would then find the respective post, and would either increment or decrement the score field by 1.  The problems with this system should be pretty obvious, under this system a user would be able to voted for things multiple times, b/c we're not tracking who has voted on what post.  It is also a problem, because our users would not be able to see what they have voted on.  So the questions arises, how do you keep track of every single time a user clicks on an up/down vote arrow?  If you think about it, every time someone votes on a piece of content, they are creating a link between their user and that piece of content on the back-end.  So now as we get further into the problem, we can start seeing a many-to-many relationship emerge, b/c every time a vote is made, that aforementioned "link" can be represented like this:

**users_posts**

======== ======== =====
user_id  post_id  vote
======== ======== =====
1        1        1
1        2        -1
======== ======== =====

So every time a user clicks on an arrow, a record is stored in the database that persists that specific user(user_id) voting on a specific post(post_id) in a way that is indicated by the 'vote' field in some way, either as a string('up or 'down') or a integer(-1 or 1).  I like the number approach better, as you can then sum all of votes for a specific post to arrive at the score of that post.  

On a side note, many-to-many relationships, or more specifically an association objects, are incredibly common for solving problems such as these, where you have a number of "links" between objects being made.  The difference between a many-to-many relationship and an association object patterns are that in SQLAlchemy, a many-to-many relationship uses a "secondary" table in order to relate two tables while an association object uses another model that inherits from the Base.  A standard many-to-many ends up looking something like this:

.. code-block:: python

    UserGroupModel = Table('users_groups', Base.metadata,
                           Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
                           Column('group_id', Integer, ForeignKey('groups.id'), primary_key=True)
    )

    class GroupModel(Base):
        __tablename__ = 'groups'

        id = Column(Integer, primary_key=True)
        name = Column(String(50))

        def __init__(self, **fields):
            self.__dict__.update(fields)

        def __repr__(self):
            return "<Group('%s', '%s')>" % (self.id,
                                            self.name)

    class UserModel(Base):
        __tablename__ = 'users'

        id = Column(Integer, primary_key=True)
        identifier = Column(String(50))
        password = Column(String(40))
        groups = relationship(GroupModel,
                              secondary=UserGroupModel,
                              backref="users")

        def __init__(self, **fields):
            self.__dict__.update(fields)

        def __repr__(self):
            return "<User('%s', '%s')>" % (self.id,
                                           self.identifier)

While on the other hand, an association object uses a completely separate model, which inherits from the base just like the rest of them, in order to create the relationship.  This opens up the possibility to stick other values on the intermediary model which store extra data about the link.  We'll use this concept to store whether a vote is an up/down vote later. One caveat of the association object pattern, however, is that you have to interact with the intermediary model directly and use association proxies, as opposed to it being completely transparent in a standard many-to-many.  You can read more on this topic `here <http://www.sqlalchemy.org/docs/orm/extensions/associationproxy.html?highlight=association%20proxy#simplifying-association-objects>`_.  From the demo code, this is an example of an association object:

.. code-block:: python

    class ObjectsModel(Base):
        __tablename__ = 'objects'
        
        id = Column(Integer, primary_key=True)
        score = Column(Integer(100), default=0)
        voted_users = association_proxy('users_objects', 'users')
    
        def __init__(self, **fields):
            self.__dict__.update(fields)
    
        def __repr__(self):
            return "<Objects('%s')>" % (self.id)
    
    class UsersModel(Base):
        __tablename__ = 'users'
        
        id = Column(Integer, primary_key=True)
        voted_objects = association_proxy('users_objects', 'objects')
    
        def __init__(self, **fields):
            self.__dict__.update(fields)
    
        def __repr__(self):
            return "<Users('%s', '%s', '%s')>" % (self.id)
    
    class UsersObjectsModel(Base):
        __tablename__ = 'users_objects'
        
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('users.id'))
        object_id = Column(Integer, ForeignKey('objects.id'))
        vote = Column(Integer(1))
        
        users = relationship(UsersModel,
                             backref="users_objects")
        objects = relationship(ObjectsModel,
                               backref="users_objects")
    
        def __init__(self, **fields):
            self.__dict__.update(fields)
    
        def __repr__(self):
            return "<UsersComments('%s', '%s', '%s')>" % (self.user_id,
                                                          self.object_id,
                                                          self.vote) 

For another example of a use of association objects, recently I made an app that is used for making Dota 2 guides.  In this app, I had a number of users adding items from a list of about 125 into different sections of each guide.  I used an association object to create a relationship between my "guide" model and my "user" model each time someone dragged an item into a section of a guide.  This got me to a point where I could see which items were added to which guide; however, I needed to see exactly which section of the guide the item was added to, so I added some metadata to the relationship.  Putting a "section" field on the intermediary model allowed me to see exactly which section of the guide the user added the item to.  I tend to always use association objects as opposed to many-to-many relationships, as it gives me the option add metadata to the relationship later on.


Pyramid-Specific Stuff
----------------------
So now we know how the data is represented in the database, and how we keep track of each user voting on content. Now let's look at the stuff we add to our Pyramid configuration.  Believe it or not, you can get away with only having to add a single route and a single view to your application.  Let's check out the route first:

.. code-block:: python

    config.add_route('toggle_vote', '/toggle_vote/{user_id}/{object_id}/{vote}')

Knowing how it looks in the database, this looks pretty appropriate, right?  Every time a user votes on something, we make this request and pass in the id of the user(could alternately be their username or something), the id of the object(comment, post, article, etc), and the orientation of their vote.  This can be directed to from a link, but the cleaner approach is to spawn an AJAX request each time a user clicks on an up/down arrow, which is the approach I take in the demo.  Either way, once you make a request that matches this route, a view like this is called:

.. code-block:: python

    class ToggleVoteHandler(object):
        def __init__(self, request):
            self.request = request
            self.here = request.environ['PATH_INFO']
            self.matchdict = request.matchdict
            
        @view_config(route_name='toggle_vote', renderer='json')
        def toggle_vote(self):
            user_id = self.matchdict['user_id']
            object_id = self.matchdict['object_id']
            vote = self.matchdict['vote']
            
            db = self.request.db
            voted_object = db.query(ObjectsModel).filter_by(id=object_id).first()
            if vote=='up':
                vote = 1
            elif vote=='down':
                vote = -1
            else:
                return {'status' : 'unchanged', 'score' : voted_object.score}
            
            users_objects = db.query(UsersObjectsModel).filter_by(user_id=user_id,
                                                                  object_id=object_id).first()
            # Vote exists                                                             
            if users_objects:
                if users_objects.vote != vote:
                    users_objects.vote = vote
                    db.flush()
                    status = 'changed'
                else:
                    db.delete(users_objects)
                    db.flush()
                    status = 'deleted'
                    
            # Vote doesn't exist
            else:
                users_objects = UsersObjectsModel(user_id=user_id,
                                                  object_id=object_id,
                                                  vote=vote)
                db.add(users_objects)
                db.flush()
                status = 'added'
            
            score = self.calculateScore(voted_object)
            voted_object.score = score
            db.flush()
            return {'status' : status, 'score' : score}
            
        def calculateScore(self, voted_object):
            score = 0
            for users_objects in voted_object.users_objects:
                score += users_objects.vote
            return score 

So this view pretty much does all of the business logic we have talked about, plus a little extra.  It get's the user_id, object_id, and the vote through the matchdict, and makes sure that the vote is a valid value of '-1' or '1'.  Then it tries to find out if the user has voted on this specific object before.  If they have, it then further checks if the vote is of the same orientation or not, and either changes the vote or deletes the relationship(if the user clicks on the same orientation a second time, they are trying to remove their vote) respectively.  If they haven't voted on this object before, the view creates a link between the user and the object with the specified vote orientation.  Lastly all of the votes related with the object are summed and the score is return in a JSON object, as well as a status string that I included for the front-end.  So this process should be fairly straight forward, once you get the hang of the way the data is managed in the database, as the view is the element of the application that is actually doing all of the heavy lifting to store/correct the data.  Now all that is left is the front-end.

Let's Get the Client Talking To Us
----------------------------------
The last step in getting this system to work, is we need a way to get the client to tell us when a user clicks on a up or down arrow.  As I mentioned before, you could make each arrow an anchor tag to the appropriate view, but this wouldn't provide for a very responsive interface.  So what I have done is, added an onclick event to the up/down arrows, which sends a request to the Pyramid app which is handled by the 'toggle_vote' view.  Here is what the voting buttons look like next to each post in the demo.

.. code-block:: html

    <div class="vote">
        <div class="${up}" onClick="javascript: toggle_vote(this, ${user_id}, ${object.id}, 'up');"></div>
        <div class="${down}" onClick="javascript: toggle_vote(this, ${user_id}, ${object.id}, 'down');"></div>
    </div>

This calls a javascript function called, appropriately, 'toggle_vote', which does all of the interfacey changes once a vote is made.  It looks like this:

.. code-block:: javascript

    toggle_vote = function(node, user_id, object_id, vote) {
        object_vote = node.parentNode;
        object = object_vote.parentNode;
            
        removeActiveClass = function(node) {
            index = node.className.indexOf(" active");
            node.className = (index != -1) ? node.className.substring(0, index) : node.className;
        };
        
        addActiveClass = function(node) {
            node.className = node.className + " active";
        };
        
        removeAllActiveClasses = function(parent) {
            $.each(parent.children, function(index, child) {
                removeActiveClass(child); 
            });
        };
    
        setScore = function(score) {
            object_score = undefined;
            $.each(object.children, function(index, child) {
                if (child.className == "score") {
                    object_score = child;   
                }
            });
            object_score.innerHTML = String(score);
        };
        
        toggleVoteCallback = function(data) {
            if (data.status != "unchanged") {
                if (node.className.indexOf("active") != -1) {
                    removeAllActiveClasses(object_vote);
                }
                else {
                    removeAllActiveClasses(object_vote);
                    addActiveClass(node);
                }
            }
            
            setScore(data.score);
        };
            
        $.ajax({
        type: "GET",
            url: "/toggle_vote/" + user_id + "/" + object_id + "/" + vote,
            success: toggleVoteCallback
        });
    };

I'm sure there is an easier way to do some of these things with some jQuery magic unknown to me, but essentially what it does, is it first sends a AJAX GET request to the 'toggle_vote' view that we talked about previously.  Then according to the status string, it changes the up/down arrows to either be inactive or active, which translates to either being of the 'active' class or not.  Lastly it takes the current score of the object(the sum of all of its votes) and updates the part of the interface that displays the score.  I decided on going with this method, as it ensures an updated value of the score; however, this also means that if a user votes on something at the same time as another user, one of them will see the score go up by two, which is not a desired outcome and might confuse people, so something to keep in mind. So that's that. The full process of adding social voting to your site.

**Note On Security:  This demo is not exactly secure, because we can't verify that a request is coming from the user specified as the 'user_id'.  So to improve this example, we could add a CSRF check or something to verify that it truly is the user voting on an object.  That could be for another day.
