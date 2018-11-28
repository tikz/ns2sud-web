

  Vue.component('todo-item', {
  // The todo-item component now accepts a
  // "prop", which is like a custom attribute.
  // This prop is called todo.
  props: ['todo'],
  template: '<li>{{ todo.text }}</li>'
})

  Vue.component('match-item', {
    props: ['todo'],
    template: '<tr><th><a href="#">{{ match.roundId }}</a></th><td>{{ match.roundDate}}</td><td>8v8</td><td>{{ match.mapName }}</td><td>Khaara</td><td>23:12</td></tr>'
  })