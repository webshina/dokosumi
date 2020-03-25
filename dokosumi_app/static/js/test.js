function dragMoveListener (event) {
    var target = event.target
    // keep the dragged position in the data-x/data-y attributes
    var x = (parseFloat(target.getAttribute('data-x')) || 0 ) + event.dx
    var y = (parseFloat(target.getAttribute('data-y')) || 0 ) + event.dy
  
    // translate the element
    target.style.webkitTransform =
      target.style.transform =
        'translate(' + x + 'px, ' + y + 'px)'
  
    // update the posiion attributes
    target.setAttribute('data-x', x)
    target.setAttribute('data-y', y)
}

var angleScale = {
    angle: 0,
    scale: 1
    }
    
var gestureArea = document.getElementById('gesture-area')
var scaleElement = document.getElementById('scale-element')

interact(gestureArea)
    .gesturable({
        // enable inertial throwing
        inertia: true,

        // keep the element within the area of it's parent
        modifiers: [
            interact.modifiers.restrictRect({
                restriction: document.getElementById('img'),
                endOnly: true
            })
        ],
        
        // enable autoScroll
        autoScroll: true,

        onstart: function (event) {
            angleScale.angle -= event.angle
            },
        
        onmove: function (event) {

            // document.body.appendChild(new Text(event.scale))
            var currentAngle = event.angle + angleScale.angle
            var currentScale = event.scale * angleScale.scale

            scaleElement.style.webkitTransform =
            scaleElement.style.transform =
                'rotate(' + currentAngle + 'deg)' + 'scale(' + currentScale + ')'
            
            // uses the dragMoveListener from the draggable demo above
            dragMoveListener(event)

            },

            onend: function (event) {
            angleScale.angle = angleScale.angle + event.angle
            angleScale.scale = angleScale.scale * event.scale
        }

    })

    .draggable({
        // enable inertial throwing
        inertia: true,
        // keep the element within the area of it's parent
        modifiers: [
        interact.modifiers.restrictRect({
            restriction: document.getElementById('img'),
            endOnly: true
        })
        ],
        // enable autoScroll
        autoScroll: true,
        
        // call this function on every dragmove event
        onmove: function (event) {
            dragMoveListener(event)
        },
        
    })

$(document).on('click', '#add_stmp_btn', function() {
    var stmp_txet = document.getElementById('stmp_text');
    var stmp_txet_fix = document.getElementById('stmp_text_fix');

    stmp_text_fix.innerHTML = stmp_text.value
})

$(document).on('click', '#commit_stmp_btn', function() {
    var canvas = document.getElementById('canvas');
    var context = canvas.getContext('2d');

    context.fillRect(20,40,200,200);
})