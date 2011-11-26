<div class="objects">
    % for object in objects:
        <%
        user_id = 1
        up = "up"
        down = "down"
        vote = ""

        for users_objects in object.users_objects:
            if user_id == users_objects.user_id and object.id == users_comments.object_id:
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
            <div class="score">${object.score}</div>
            <div class="rate">
                <div class="${up}" onClick="javascript: toggle_vote(this, ${user_id}, ${object.id}, 'up');"></div>
                <div class="${down}" onClick="javascript: toggle_vote(this, ${user_id}, ${object.id}, 'down');"></div>
            </div>
        </div>
    % endfor
</div>