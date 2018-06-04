<template>
  <div>
    <h2>{{ `Срочные контракты (сессия #${selectedSession._id})` }}</h2>
    <date-view
      v-if="selectedSession"
      :dates="[selectedSession.startDate, selectedSession.finishDate]"/>
    <vm-tabs>
      <vm-tab-pane
        label="схема">
        <div class="futures__selectors">
          <date-selector
            :value="selectedDate"
            :prev-date="selectedSession.startDate"
            :on-select="onSelectDate"
            :from-date="selectedSession.startDate"
            :to-date="selectedSession.finishDate"/>
          <div
            style="display: flex; flex-direction: column;">
            <button
              class="futures__selector_up-btn"
              @click="dayUp"/>
            <button
              class="futures__selector_down-btn"
              @click="dayDown"/>
          </div>
          <multiselect
            v-model="hour"
            :options="hours"
            :placeholder="'час'"
            :allow-empty="false"
            select-label=""
            selected-label=""
            deselect-label=""
            class="futures__multiselect-wrapper"/>
          <div
            style="display: flex; flex-direction: column;">
            <div
              style="display: flex; flex-direction: column;">
              <button
                class="futures__selector_up-btn"
                @click="hourUp"/>
              <button
                class="futures__selector_down-btn"
                @click="hourDown"/>
            </div>
          </div>
          <template
            v-if="selectedSession.status === 'closed'">
            <input
              v-model="limitType"
              type="radio"
              value="SECTION_FLOW_LIMIT_EX_mod"
              @change="updateLimitType">
            <span>До расчета</span>
            <input
              v-model="limitType"
              type="radio"
              value="SECTION_FLOW_LIMIT_DAM"
              @change="updateLimitType">
            <span>После расчета</span>
          </template>
        </div>
        <map-view
          :arm-cons="getCountryResultsFutures(selectedDate, hour, 'ARM', 'buy', limitType)"
          :arm-gen="getCountryResultsFutures(selectedDate, hour, 'ARM', 'sell', limitType)"
          :blr-cons="getCountryResultsFutures(selectedDate, hour, 'BLR', 'buy', limitType)"
          :blr-gen="getCountryResultsFutures(selectedDate, hour, 'BLR', 'sell', limitType)"
          :kaz-cons="getCountryResultsFutures(selectedDate, hour, 'KAZ', 'buy', limitType)"
          :kaz-gen="getCountryResultsFutures(selectedDate, hour, 'KAZ', 'sell', limitType)"
          :kaz-kgz-section-limits="getSectionLimits(hour, 'KAZ-KGZ')"
          :kaz-kgz="getSectionFlowFutures(selectedDate, hour, 'KAZ-KGZ', limitType)"
          :kgz-cons="getCountryResultsFutures(selectedDate, hour, 'KGZ', 'buy', limitType)"
          :kgz-gen="getCountryResultsFutures(selectedDate, hour, 'KGZ', 'sell', limitType)"
          :rus-arm="getSectionFlowFutures(selectedDate, hour, 'RUS-ARM', limitType)"
          :rus-arm-section-limits="getSectionLimits(hour, 'RUS-ARM')"
          :rus-blr="getSectionFlowFutures(selectedDate, hour, 'RUS-BLR', limitType)"
          :rus-blr-section-limits="getSectionLimits(hour, 'RUS-BLR')"
          :rus-cons="getCountryResultsFutures(selectedDate, hour, 'RUS', 'buy', limitType)"
          :rus-gen="getCountryResultsFutures(selectedDate, hour, 'RUS', 'sell', limitType)"
          :rus-kaz="getSectionFlowFutures(selectedDate, hour, 'RUS-KAZ', limitType)"
          :rus-kaz-section-limits="getSectionLimits(hour, 'RUS-KAZ')"/>
      </vm-tab-pane>
      <vm-tab-pane
        label="контракты">
      </vm-tab-pane>
    </vm-tabs>
  </div>
</template>

<script>
import { mapGetters, mapActions } from 'vuex';
import { compareAsc, addDays } from 'date-fns';
import { VmTabs, VmTabPane } from 'vue-multiple-tabs';
import Multiselect from 'vue-multiselect';
import DateView from '../common/DateView.vue';
import DateSelector from '../common/DateSelector.vue';
import MapView from '../common/MapView.vue';

export default {
  name: 'FuturesPhaseView',
  components: {
    DateSelector,
    DateView,
    MapView,
    Multiselect,
    VmTabPane,
    VmTabs,
  },
  data() {
    let i = 0;
    return {
      limitType: 'SECTION_FLOW_LIMIT_EX_mod',
      hour: '0',
      hours: new Array(24).fill().map(() => (i++).toString()), // eslint-disable-line
      selectedDate: null,
    };
  },
  computed: {
    ...mapGetters('common', ['selectedSession', 'getSectionLimits', 'getSectionFlowFutures', 'getCountryResultsFutures']),
  },
  created() {
    this.selectedDate = this.selectedSession.startDate;
    this.updateLimitType();
    this.queryAllFutures();
  },
  methods: {
    ...mapActions('common', ['querySectionLimits', 'queryAllFutures']),
    onSelectDate(d) {
      this.selectedDate = d;
      this.updateLimitType();
    },
    updateLimitType() {
      this.querySectionLimits({
        limitType: this.limitType,
        targetDate: this.selectedDate,
      });
    },
    dayUp() {
      if (!compareAsc(this.selectedDate, this.selectedSession.startDate)) return;
      this.onSelectDate(addDays(this.selectedDate, -1));
    },
    dayDown() {
      if (!compareAsc(this.selectedDate, this.selectedSession.finishDate)) return;
      this.onSelectDate(addDays(this.selectedDate, 1));
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
.futures__multiselect-wrapper {
  display: inline-block !important;
  width: 100px !important;
}

.futures__selectors {
  display: flex;
  align-items: center;
}

.futures__selectors > * {
  margin: 0 5px;
}

.futures__selector_up-btn:before {
  position: relative;
  display: block;
  content: "";
  margin-bottom: 4px;
  border: solid 5px transparent;
  border-bottom-color: #999;
  height: 0;
  width: 0;
}

.futures__selector_down-btn:before {
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
