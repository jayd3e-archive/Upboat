$(window).ready(function() {
    activateArrows = function(image_gallery) {
        $.each(gallery_children, function(id, childNode) {
            if(childNode.className.indexOf("arrow") != -1) {
                arrow = childNode;
                arrow.style.display = "block";
            }
        });
    };

    //Initialize arrows if present.
    image_galleries = document.getElementsByClassName("image_gallery");
    
    $.each(image_galleries, function(index, image_gallery) {
        gallery_children = image_gallery.children;
        image_slide = undefined;
        $.each(gallery_children, function(id, childNode) {
            if(childNode.className == "image_slide") {
                image_slide = childNode;
            }
        });

        index = image_slide.children.length - 1;
        farthestRightElement = image_slide.children[index];
        rightEdgeOffset = farthestRightElement.offsetLeft + farthestRightElement.offsetWidth;

        if(rightEdgeOffset > image_gallery.offsetWidth) {
            activateArrows(image_gallery);
        }
    });
});

slide = function(node, direction) {
    step_size = 150;
    
    image_gallery = node.parentNode;
    gallery_children = image_gallery.children;
    image_slide = undefined;
    $.each(gallery_children, function(id, childNode) {
        if(childNode.className == "image_slide") {
            image_slide = childNode;   
        }
    });
    left = image_slide.style.left === "" ? "0px" : image_slide.style.left;
    left_int = parseInt(left);
    
    index = image_slide.children.length - 1;
    farthestRightElement = image_slide.children[index];
    rightEdgeOffset = farthestRightElement.offsetLeft + farthestRightElement.offsetWidth;
    gallery_width = image_gallery.offsetWidth;
    
    if(direction == "left") {
        step = step_size;
        new_left = left_int + step;
        if(new_left > 0) {
            step = step_size - new_left;
            new_left = left_int + step;
        }
    }
    else {
        step = -1 * step_size;
        new_left = left_int + step;
        if ((new_left + rightEdgeOffset) < gallery_width) {
            remainder =  gallery_width - (new_left + rightEdgeOffset);
            step = step_size - remainder;
            new_left = left_int - step;
        }
    }
    
    image_slide.style.left = String(new_left) + "px";
};

toggle_vote = function(node, user_id, comment_id, vote) {
    comment_rate = node.parentNode;
    comment = comment_rate.parentNode;
        
    removeActiveClass = function(node) {
        index = node.className.indexOf("active");
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
        comment_score = undefined;
        $.each(comment.children, function(index, child) {
            if (child.className == "comment_score") {
                comment_score = child;   
            }
        });
        comment_score.innerHTML = String(score);
    };
    
    toggleVoteCallback = function(data) {
        if (data.status != "unchanged") {
            if (node.className.indexOf("active") != -1) {
                removeAllActiveClasses(comment_rate);
            }
            else {
                removeAllActiveClasses(comment_rate);
                addActiveClass(node);
            }
        }
        
        setScore(data.score);
    };
        
	$.ajax({
		type: "GET",
	    url: "/toggle_vote/" + user_id + "/" + comment_id + "/" + vote,
        success: toggleVoteCallback
	});
};