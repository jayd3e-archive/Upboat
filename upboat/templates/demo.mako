<!DOCTYPE html>
<html>
    <head>
        <title>${title}</title>
        <link rel="stylesheet" type="text/css" href="/static/css/style.css" />
        <link rel="stylesheet" type="text/css" href="/static/css/type.css" />
        <script type="text/javascript" src="/static/js/jquery.js"></script>
        <script type="text/javascript" src="/static/js/upboat.js"></script>
    </head>
    <body>
        <div class="add">
            <form method='POST' action=''>
                <input type='submit' name='submit' value='Add Object'/>
            </form>
        </div>
        <div class="objects">
            % for object in objects:
                <%
                # user_id would be replaced by the id of your actual user
                user_id = 1
                up = "up"
                down = "down"
                vote = ""

                for users_objects in object.users_objects:
                    if user_id == users_objects.user_id and object.id == users_objects.object_id:
                        vote = users_objects.vote
                        if vote == 1:
                            up = up + " active"
                        elif  vote == -1:
                            down = down + " active"
                        break
                    else:
                        continue
                %>
                <div class="object">
                    <div class="id">Object #${object.id}</div>
                    <div class="vote">
                        <div class="${up}" onClick="javascript: toggle_vote(this, ${user_id}, ${object.id}, 'up');"></div>
                        <div class="${down}" onClick="javascript: toggle_vote(this, ${user_id}, ${object.id}, 'down');"></div>
                    </div>
                    <div class="score">${object.score}</div>
                </div>
            % endfor
        </div>
    </body>
</html>