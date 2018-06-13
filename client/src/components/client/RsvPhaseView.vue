<template>
  <div>
    <h2>{{ `Сессия РСВ #${selectedSession._id}` }}</h2>
    <date-view
      v-if="selectedSession"
      :dates="[selectedSession.startDate, selectedSession.finishDate]"/>
    <vm-tabs
      :value="selectedTab">
      <vm-tab-pane
        label="схема">
        <div class="rsv__selectors">
          <label>Час:</label>
          <multiselect
            v-model="hour"
            :options="hours"
            :placeholder="'час'"
            :allow-empty="false"
            select-label=""
            selected-label=""
            deselect-label=""
            class="rsv__multiselect-wrapper"/>
          <div style="display: inline-block;">
            <div
              style="display: flex; flex-direction: column;">
              <button
                class="rsv__selector_up-btn"
                @click="hourUp"/>
              <button
                class="rsv__selector_down-btn"
                @click="hourDown"/>
            </div>
          </div>
        </div>
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
          :rus-arm-section-limits="getSectionLimits(parseInt(hour, 0), 'RUS-ARM')"
          :rus-blr-section-limits="getSectionLimits(parseInt(hour, 0), 'RUS-BLR')"
          :rus-kaz-section-limits="getSectionLimits(parseInt(hour, 0), 'RUS-KAZ')"
          :kaz-kgz-section-limits="getSectionLimits(parseInt(hour, 0), 'KAZ-KGZ')"
          :node-arm1-price="getNodePrice(parseInt(hour, 0), 'ARM', 'RUS-ARM', 'sell')"
          :node-blr1-price="getNodePrice(parseInt(hour, 0), 'BLR', 'RUS-BLR', 'sell')"
          :node-rus1-price="getNodePrice(parseInt(hour, 0), 'RUS', 'RUS-ARM', 'sell')"
          :node-rus2-price="getNodePrice(parseInt(hour, 0), 'RUS', 'RUS-BLR', 'sell')"
          :node-rus3-price="getNodePrice(parseInt(hour, 0), 'RUS', 'RUS-KAZ', 'sell')"
          :node-kaz1-price="getNodePrice(parseInt(hour, 0), 'KAZ', 'RUS-KAZ', 'sell')"
          :node-kaz2-price="getNodePrice(parseInt(hour, 0), 'KAZ', 'KAZ-KGZ', 'sell')"
          :node-kgz1-price="getNodePrice(parseInt(hour, 0), 'KGZ', 'KAZ-KGZ', 'sell')"
          />
      </vm-tab-pane>
      <vm-tab-pane label="заявка РСВ">
        <bid-editor
          v-if="selectedSession.status === 'open' || bid"
          :bid="bid"/>
      </vm-tab-pane>
    </vm-tabs>
  </div>
</template>

<script>
import { mapActions, mapGetters, mapState } from 'vuex';
import { VmTabs, VmTabPane } from 'vue-multiple-tabs';
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
      selectedTab: 0,
    };
  },
  computed: {
    ...mapState('common', ['bid', 'queringBid', 'spotResults']),
    ...mapGetters('common', ['selectedSession', 'getCountryResults', 'getNodePrice', 'getSectionLimits']),
  },
  watch: {
    selectedSession() {
      if (this.selectedSession.status === 'open') {
        this.selectedTab = 1;
      }
    },
  },
  created() {
    this.queryBid();
    this.queryResults();
    this.querySectionLimits({ limitType: 'SECTION_FLOW_LIMIT_DAM_mod' });
    this.queryMgp();
    this.queryAllFutures();
  },
  methods: {
    ...mapActions('common', ['queryMgp', 'queryBid', 'queryResults', 'querySectionLimits', 'queryAllFutures']),
    getSectionFlow(hour, sectionCode) {
      return this.spotResults && this.spotResults.hours[hour].sections
        .find(({ code }) => code === sectionCode).flow;
    },
    hourUp() {
      if (this.hour === this.hours[0]) return;
      this.hour = this.hours[this.hours.indexOf(this.hour) - 1];
    },
    hourDown() {
      if (this.hour === this.hours[this.hours.length - 1]) return;
      this.hour = this.hours[this.hours.indexOf(this.hour) + 1];
    },
  },
};
</script>

<style>
.rsv__multiselect-wrapper {
  display: inline-block !important;
  width: 30% !important;
  flex: 1;
  margin: 0 10px;
}

.rsv__selectors {
  display: flex;
  align-items: center;
  max-width: 300px;
  justify-content: space-between;
}

.rsv__selector_up-btn:before {
  position: relative;
  display: block;
  content: "";
  margin-bottom: 4px;
  border: solid 5px transparent;
  border-bottom-color: #999;
  height: 0;
  width: 0;
}

.rsv__selector_down-btn:before {
  position: relative;
  display: block;
  content: "";
  margin-top: 4px;
  border: solid 5px transparent;
  border-top-color: #999;
  height: 0;
  width: 0;
}
</style>
