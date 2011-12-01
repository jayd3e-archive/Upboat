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