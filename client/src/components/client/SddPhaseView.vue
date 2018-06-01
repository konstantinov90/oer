<template>
  <div>
    <h2>{{ `Свободные договоры (СД) (сессия #${selectedSession._id})` }}</h2>
    <date-view
      v-if="selectedSession"
      :dates="[selectedSession.startDate, selectedSession.finishDate]"/>
    <vm-tabs>
      <vm-tab-pane
        label="договоры">
        <button
          v-if="!editorVisible && selectedSession.status === 'open'"
          class="new-sdd-btn"
          @click="toggleEditorVisible">
          +
        </button>
        <sdd-list-view />
      </vm-tab-pane>
      <vm-tab-pane
        label="схема">
        <div class="sdd__selectors">
          <date-selector
            :value="selectedDate"
            :prev-date="selectedSession.startDate"
            :on-select="onSelectDate"
            :from-date="selectedSession.startDate"
            :to-date="selectedSession.finishDate"/>
          <div
            style="display: flex; flex-direction: column;">
            <button
              class="sdd__selector_up-btn"
              @click="dayUp"/>
            <button
              class="sdd__selector_down-btn"
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
            class="sdd__multiselect-wrapper"/>
          <div
            style="display: flex; flex-direction: column;">
            <div
              style="display: flex; flex-direction: column;">
              <button
                class="sdd__selector_up-btn"
                @click="hourUp"/>
              <button
                class="sdd__selector_down-btn"
                @click="hourDown"/>
            </div>
          </div>
          <template
            v-if="selectedSession.status === 'closed'">
            <input
              v-model="limitType"
              type="radio"
              value="SECTION_FLOW_LIMIT_FC"
              @change="updateLimitType">
            <span>До расчета</span>
            <input
              v-model="limitType"
              type="radio"
              value="SECTION_FLOW_LIMIT_EX"
              @change="updateLimitType">
            <span>После расчета</span>
          </template>
        </div>
        <map-view
          :arm-cons="getCountryResultsSdd(selectedDate, hour, 'ARM', 'buy', limitType)"
          :arm-gen="getCountryResultsSdd(selectedDate, hour, 'ARM', 'sell', limitType)"
          :blr-cons="getCountryResultsSdd(selectedDate, hour, 'BLR', 'buy', limitType)"
          :blr-gen="getCountryResultsSdd(selectedDate, hour, 'BLR', 'sell', limitType)"
          :kaz-cons="getCountryResultsSdd(selectedDate, hour, 'KAZ', 'buy', limitType)"
          :kaz-gen="getCountryResultsSdd(selectedDate, hour, 'KAZ', 'sell', limitType)"
          :kaz-kgz-section-limits="getSectionLimits(hour, 'KAZ-KGZ')"
          :kaz-kgz="getSectionFlowSdd(selectedDate, hour, 'KAZ-KGZ', limitType)"
          :kgz-cons="getCountryResultsSdd(selectedDate, hour, 'KGZ', 'buy', limitType)"
          :kgz-gen="getCountryResultsSdd(selectedDate, hour, 'KGZ', 'sell', limitType)"
          :rus-arm="getSectionFlowSdd(selectedDate, hour, 'RUS-ARM', limitType)"
          :rus-arm-section-limits="getSectionLimits(hour, 'RUS-ARM')"
          :rus-blr="getSectionFlowSdd(selectedDate, hour, 'RUS-BLR', limitType)"
          :rus-blr-section-limits="getSectionLimits(hour, 'RUS-BLR')"
          :rus-cons="getCountryResultsSdd(selectedDate, hour, 'RUS', 'buy', limitType)"
          :rus-gen="getCountryResultsSdd(selectedDate, hour, 'RUS', 'sell', limitType)"
          :rus-kaz="getSectionFlowSdd(selectedDate, hour, 'RUS-KAZ', limitType)"
          :rus-kaz-section-limits="getSectionLimits(hour, 'RUS-KAZ')"/>
      </vm-tab-pane>
    </vm-tabs>
    <div v-if="editorVisible">
      <div
        :style="`height: ${backgroundHeight}`"
        class="modal-background"/>
      <div class="modal-foreground">
        <sdd-editor
          :close-fn="toggleEditorVisible"/>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex';
import { VmTabs, VmTabPane } from 'vue-multiple-tabs';
import { addDays, compareAsc } from 'date-fns';
import Multiselect from 'vue-multiselect';
import SddListView from '../common/SddListView.vue';
import SddEditor from '../common/SddEditor.vue';
import DateView from '../common/DateView.vue';
import DateSelector from '../common/DateSelector.vue';
import MapView from '../common/MapView.vue';

export default {
  name: 'SddPhaseView',
  components: {
    DateSelector,
    DateView,
    MapView,
    Multiselect,
    SddEditor,
    SddListView,
    VmTabPane,
    VmTabs,
  },
  data() {
    let i = 0;
    return {
      limitType: 'SECTION_FLOW_LIMIT_FC',
      editorVisible: false,
      backgroundHeight: '100%',
      hour: '0',
      hours: new Array(24).fill().map(() => (i++).toString()),
      selectedDate: null,
    };
  },
  computed: {
    ...mapGetters('common', ['selectedSession', 'getSectionFlowSdd', 'getSectionLimits', 'getCountryResultsSdd']),
  },
  created() {
    this.selectedDate = this.selectedSession.startDate;
    window.addEventListener('scroll', this.updateBackgroundHeight);
    this.updateLimitType();
    this.queryAllSdd();
  },
  destroyed() {
    window.removeEventListener('scroll', this.updateBackgroundHeight);
  },
  methods: {
    ...mapActions('common', ['querySectionLimits', 'queryAllSdd']),
    updateBackgroundHeight() {
      this.backgroundHeight = `${window.innerHeight + window.pageYOffset}px`;
    },
    toggleEditorVisible() {
      this.editorVisible = !this.editorVisible;
    },
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
      this.selectedDate = addDays(this.selectedDate, -1);
    },
    dayDown() {
      if (!compareAsc(this.selectedDate, this.selectedSession.finishDate)) return;
      this.selectedDate = addDays(this.selectedDate, 1);
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
.new-sdd-btn {
  height: 48px;
  width: 48px;
  border-radius: 24px;
  font-size: 40px;
  background: coral;
  color: white;
  box-shadow: 3px 3px gray;
  margin: 0 48%;
}

.modal-background {
  position: absolute;
  top: 0;
  /* bottom: 0; */
  left: 0;
  right: 0;
  background: black;
  opacity: 0.4;
}

.modal-foreground {
  position: absolute;
  top: 0;
  /* bottom: 0; */
  left: 0;
  right: 0;
  background: white;
  margin: 40px;
  padding: 20px;
  z-index: 10;
}

.sdd__multiselect-wrapper {
  display: inline-block !important;
  width: 100px !important;
}

.sdd__selectors {
  display: flex;
  align-items: center;
}

.sdd__selectors > * {
  margin: 0 5px;
}

.sdd__selector_up-btn:before {
  position: relative;
  display: block;
  content: "";
  margin-bottom: 4px;
  border: solid 5px transparent;
  border-bottom-color: #999;
  height: 0;
  width: 0;
}

.sdd__selector_down-btn:before {
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
