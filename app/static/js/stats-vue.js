const tabMatches = Vue.component('tab-matches', {
    template: `
    <div id="matches">
        <div class="control has-icons-left has-icons-right">
        <input class="input is-large" type="email" placeholder="Filter by match id or map" v-model="filter">
        <span class="icon is-medium is-left">
            <i class="fas fa-filter"></i>
        </span>
        <span class="icon is-medium is-right">
            <i class="fas fa-check"></i>
        </span>
        </div>
        <table class="table is-fullwidth">
        <thead>
            <tr>
            <th>ID</th>
            <th>Format</th>
            <th>Map</th>
            <th class="is-hidden-mobile">Winner</th>
            <th class="is-hidden-mobile">Duration</th>
            <th>Date</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="match in data">
            <th>
                <a v-bind:href="'/stats/match/'+match.roundId">{{ match.roundId }}</a>
            </th>
            <td>{{ match.maxPlayers1 }}v{{ match.maxPlayers2 }}</td>
            <td>{{ match.mapName }}</td>
            <td class="is-hidden-mobile">
                <template v-if="match.winningTeam == 1">Marines</template>
                <template v-if="match.winningTeam == 2">Aliens</template>
            </td>
            <td class="is-hidden-mobile">{{ match.roundLength }}</td>
            <td>{{ match.roundDateH }}</td>
            </tr>
        </tbody>
        </table>
        <nav class="pagination is-centered" role="navigation" v-bind:class="[{ 'is-loading': loading }]">
        <ul class="pagination-list">
            <li v-if="currentPage > 2"><a class="pagination-link" v-on:click="currentPage = 1">1</a></li>
            <li v-if="currentPage > 3"><span class="pagination-ellipsis">&hellip;</span></li>
            <li v-if="currentPage > 1"><a class="pagination-link" v-on:click="currentPage = currentPage - 1">{{
            currentPage - 1 }}</a></li>
            <li><a class="pagination-link is-current">{{ currentPage }}</a></li>
            <li v-if="currentPage < totalPages - 1"><a class="pagination-link"
            v-on:click="currentPage = currentPage + 1">{{ currentPage + 1
            }}</a></li>
            <li v-if="currentPage < totalPages - 2"><span class="pagination-ellipsis">&hellip;</span></li>
            <li><a class="pagination-link" v-on:click="currentPage = totalPages" v-if="currentPage < totalPages">{{
            totalPages }}</a></li>
        </ul>
        </nav>
    </div>`,
    data: function () {
        return {
            data: [],
            currentPage: 0,
            totalPages: 0,
            filter: '',
            jsonEndpoint: '/stats/json/matches',
            loading: true
        }
    },
    watch: {
        filter: function () {
            router.replace({ name: 'matches', params: { filter: this.filter, page: this.currentPage } })
            this.getData(this.currentPage);
        },
        currentPage: function () {
            router.replace({ name: 'matches', params: { filter: this.filter, page: this.currentPage } })
            this.getData(this.currentPage);
        },
    },
    methods: {
        getData: function (page) {
            this.loading = true;
            var vueParent = this;
            var req_filter = vueParent.filter;
            axios.get(this.jsonEndpoint, {
                params: {
                    filter: vueParent.filter,
                    page: page
                }
            })
                .then(function (response) {
                    if (req_filter == vueParent.filter) {
                        vueParent.data = response.data.result;
                        vueParent.totalPages = response.data.total_pages;
                        vueParent.currentPage = response.data.page;
                        vueParent.loading = false;
                        if (response.data.result.length == 0) {
                            vueParent.currentPage = 1;
                        }
                    }
                })
                .catch(function (error) {
                    console.log(error);
                });
        }
    },
    created: function () {
        this.filter = this.$route.params.filter;
        this.currentPage = this.$route.params.page;
        this.getData(this.currentPage);
    }
})
const tabPlayers = Vue.component('tab-players', {
    template: `
    <div id="players">
        <div class="control has-icons-left has-icons-right">
            <input class="input is-large" type="email" placeholder="Filter by player name" v-model="filter">
            <span class="icon is-medium is-left">
                <i class="fas fa-filter"></i>
            </span>
            <span class="icon is-medium is-right">
                <i class="fas fa-check"></i>
            </span>
            </div>
            <table class="table is-fullwidth">
            <thead>
                <tr>
                <th>Steam ID</th>
                <th></th>
                <th>Name</th>
                <th class="is-hidden-mobile">Hive Skill</th>
                <th class="is-hidden-mobile">Other names</th>
                <th>Last seen</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="player in data">
                <th>
                    <a v-bind:href="'/stats/player/'+player.steamId">{{ player.steamId }}</a>
                </th>
                <td>
                    <figure class="image is-24x24" v-if="player.discordAvatar">
                        <img class="is-rounded" v-bind:src="player.discordAvatar">
                    </figure>
                </td>
                <td>{{ player.playerName }}</td>
                <td class="is-hidden-mobile">{{ player.hiveSkill }}</td>
                <td class="is-hidden-mobile">{{ player.name_list }}</td>
                <td>{{ player.lastSeenH }}</td>
                </tr>
            </tbody>
            </table>
            <nav class="pagination is-centered" role="navigation" v-bind:class="[{ 'is-loading': loading }]">
            <ul class="pagination-list">
                <li v-if="currentPage > 2"><a class="pagination-link" v-on:click="getData(1)">1</a></li>
                <li v-if="currentPage > 3"><span class="pagination-ellipsis">&hellip;</span></li>
                <li v-if="currentPage > 1"><a class="pagination-link" v-on:click="getData(currentPage - 1)">{{
                currentPage - 1 }}</a></li>
                <li><a class="pagination-link is-current">{{ currentPage }}</a></li>
                <li v-if="currentPage < totalPages - 1"><a class="pagination-link"
                v-on:click="getData(currentPage + 1)">{{ currentPage + 1
                }}</a></li>
                <li v-if="currentPage < totalPages - 2"><span class="pagination-ellipsis">&hellip;</span></li>
                <li><a class="pagination-link" v-on:click="getData(totalPages)" v-if="currentPage < totalPages">{{
                totalPages }}</a></li>
            </ul>
            </nav>
        </div>
    </div>`,
    data: function () {
        return {
            data: [],
            currentPage: 0,
            totalPages: 0,
            filter: '',
            jsonEndpoint: '/stats/json/players',
            loading: true
        }
    },
    watch: {
        filter: function () {
            router.replace({ name: 'players', params: { filter: this.filter, page: this.currentPage } })
            this.getData(this.currentPage);
        },
        currentPage: function () {
            router.replace({ name: 'players', params: { filter: this.filter, page: this.currentPage } })
            this.getData(this.currentPage);
        },
    },
    methods: {
        getData: function (page) {
            this.loading = true;
            var vueParent = this;
            var req_filter = vueParent.filter;
            axios.get(this.jsonEndpoint, {
                params: {
                    filter: vueParent.filter,
                    page: page
                }
            })
                .then(function (response) {
                    if (req_filter == vueParent.filter) {
                        vueParent.data = response.data.result;
                        vueParent.totalPages = response.data.total_pages;
                        vueParent.currentPage = response.data.page;
                        vueParent.loading = false;
                        if (response.data.result.length == 0) {
                            vueParent.currentPage = 1;
                        }
                    }
                })
                .catch(function (error) {
                    console.log(error);
                });
        }
    },
    created: function () {
        this.filter = this.$route.params.filter;
        this.currentPage = this.$route.params.page;
        this.getData(this.currentPage);
    }
})
const routes = [
    { path: '/players/:page?/:filter?', name: 'players', component: tabPlayers },
    { path: '/matches/:page?/:filter?', name: 'matches', component: tabMatches }
]

const router = new VueRouter({
    routes,
    linkActiveClass: "is-active",
})
const app = new Vue({
    router
}
).$mount('#main')