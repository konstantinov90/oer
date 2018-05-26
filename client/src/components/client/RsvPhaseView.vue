<template>
  <div>
    <h2>{{ `Сессия РСВ #${selectedSession._id}` }}</h2>
    <date-view
      v-if="selectedSession"
      :dates="[selectedSession.startDate, selectedSession.finishDate]"/>
    <vm-tabs>
      <vm-tab-pane
        v-if="selectedSession.status !== 'open'"
        label="схема">
        <label>Час:</label>
        <multiselect
          v-model="hour"
          :options="hours"
          :placeholder="'час'"
          :allow-empty="false"
          class="rsv__multiselect-wrapper"/>
        <map-view
          :rus-arm="getSectionFlow(hour, 'RUS-ARM')"
          :rus-blr="getSectionFlow(hour, 'RUS-BLR')"
          :rus-kaz="getSectionFlow(hour, 'RUS-KAZ')"
          :kaz-kgz="getSectionFlow(hour, 'KAZ-KGZ')"
          :rus-gen="getCountryResults(hour, 'RUS', 'sell')"
          :rus-cons="getCountryResults(hour, 'RUS', 'buy')"
          :blr-gen="getCountryResults(hour, 'BLR', 'sell')"
          :blr-cons="getCountryResults(hour, 'BLR', 'buy')"
          :arm-gen="getCountryResults(hour, 'ARM', 'sell')"
          :arm-cons="getCountryResults(hour, 'ARM', 'buy')"
          :kaz-gen="getCountryResults(hour, 'KAZ', 'sell')"
          :kaz-cons="getCountryResults(hour, 'KAZ', 'buy')"
          :kgz-gen="getCountryResults(hour, 'KGZ', 'sell')"
          :kgz-cons="getCountryResults(hour, 'KGZ', 'buy')"
          :rus-arm-section-limits="getSectionLimits(hour, 'RUS-ARM')"
          :rus-blr-section-limits="getSectionLimits(hour, 'RUS-BLR')"
          :rus-kaz-section-limits="getSectionLimits(hour, 'RUS-KAZ')"
          :kaz-kgz-section-limits="getSectionLimits(hour, 'KAZ-KGZ')"/>
        <button @click="testFn">test</button>
      </vm-tab-pane>
      <vm-tab-pane label="заявка РСВ">
        <bid-editor
          v-if="!queringBid && (selectedSession.status === 'open' || bid)"
          :bid="bid"/>
      </vm-tab-pane>
    </vm-tabs>
  </div>
</template>

<script>
import { mapActions, mapGetters, mapState } from 'vuex';
import { VmTabs, VmTabPane } from 'vue-multiple-tabs'
import Multiselect from 'vue-multiselect';
import BidEditor from '../common/BidEditor.vue';
import DateView from '../common/DateView.vue';
import MapView from '../common/MapView.vue';

export default {
  name: 'RsvPhaseView',
  components: {
    BidEditor,
    DateView,
    MapView,
    Multiselect,
    VmTabs,
    VmTabPane,
  },
  data() {
    let i = 0;
    return {
      hours: new Array(24).fill().map(() => (i++).toString()), // eslint-disable-line
      hour: '0',
    };
  },
  computed: {
    ...mapState('common', ['bid', 'queringBid', 'spotResults']),
    ...mapGetters('common', ['selectedSession', 'getCountryResults', 'getSectionLimits']),
  },
  created() {
    this.queryBid();
    this.queryResults();
    this.querySectionLimits();
  },
  methods: {
    ...mapActions('common', ['queryBid', 'queryResults', 'querySectionLimits']),
    getSectionFlow(hour, sectionCode) {
      return this.spotResults && this.spotResults.hours[hour].sections
        .find(({ code }) => code === sectionCode).flow;
    },
    testFn() {
      console.log(this.getSectionLimits(0, 'RUS-BLR'))
    },
  },
};
</script>

<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>

<style>
  .vm-tabs__item,
  .vm-tabs__item.is-active {
    color: rgb(101,104,155) !important;
    font-size: 1rem;
  }

  .vm-tabs__header,
  .vm-tabs__active.is-triangle::before {
    border-bottom-color: rgb(221,234,255) !important;
  }

  .rsv__multiselect-wrapper {
    width: 30%;
    display: inline-block;
  }
</style>
