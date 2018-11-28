$("body").velocity({
  backgroundPositionY: "100%",
}, {
    duration: 60000,
    easing: "linear"
  })

$("#black").velocity({
  opacity: "0.3",
}, {
    duration: 3000,
    easing: "linear"
  });

$(".container").css('opacity', '0').velocity({
  opacity: "1",
}, {
    duration: 1000,
    easing: "linear"
  });
$(".main-navbar").velocity({
  scale: "0",
}, {
    duration: 1000,
    easing: "linear"
  });

$("#discord-glow").velocity({
  opacity: [0, "linear", 1]
}, {
    duration: 1000,
    loop: true
  });

$("#main-navbar .navbar-item").hover(function () {
  $(this).find(".icon").velocity({
    "font-size": "22px",
    "color": "#00aeff"
  }, {
      duration: 100,
      easing: "easeInQuad"
    });

}, function () {
  $(this).find(".icon").velocity({
    "font-size": "16px",
    "color": "#fff",
  }, {
      duration: 100,
      easing: "easeOutQuad"
    });
});

$('a.navbar-item').click(function (e) {
  e.preventDefault();
  newLocation = this.href;
  $('#black').velocity("stop", true).velocity({
    "opacity": "1"
  }, {
      duration: 100,
      easing: "linear"
    });

  $('#graph_chart').velocity("stop", true).velocity({
    "height": ["0px", "500px"]
  }, {
      duration: 500,
      easing: "easeInSine"
    });

  $('.container, footer').velocity("stop", true).velocity({
    "opacity": "0"
  }, {
      duration: 500,
      easing: "linear",
      complete: function () { window.location = newLocation; }
    });
});