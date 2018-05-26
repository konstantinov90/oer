<template>
  <div>
    <!-- <span>{{ hasResults }}</span> -->
    <template v-if="!adminSession && !hasResults">
      <button
        :disabled="!bidReady()"
        @click="saveBid">
        Сохранить</button>
      <button
        :disabled="!bid"
        @click="removeBid">
        Удалить</button>
    </template>
    <h3>{{ title }}</h3>
    <div
      :style="getStyle"
      class="bid-editor">
      <span
        v-if="hasResults"
        style="grid-row: span 2;">
        Тип
      </span>
      <span style="grid-row: span 2;">Час</span>
      <span style="grid-row: span 2;">
        <span style="font-size: 25px;">&Sigma;</span> дог
      </span>
      <span style="grid-row: span 2;">Объем</span>
      <span :style="`grid-column: span ${sections.length};`">Цены</span>
      <span
        v-if="!hasResults"
        style="grid-row: span 2;"/>
      <span
        v-for="section in sections"
        :key="section">
        {{ section }}
      </span>
      <template v-for="hour in hours">
        <span
          v-if="hasResults"
          :key="`type_${hour}`">
          Заявка
        </span>
        <span :key="`hr_${hour}`">{{ hour }}</span>
        <span/>
        <input
          :key="`vol_${hour}`"
          :class="isVolumeValid(hour)"
          :value="getVolume(hour)"
          :disabled="hasResults"
          @input="setVolume(hour, $event)">
        <input
          v-for="section in sections"
          :key="`${section}_${hour}`"
          :class="isPriceValid(hour, section)"
          :value="getPrice(hour, section)"
          :disabled="isInputDisabled(section) || hasResults"
          @input="setPrice(hour, section, $event)">
        <button
          v-tooltip.left="'продлить значения до конца'"
          v-if="!hasResults"
          :key="`btn_${hour}`"
          style="cursor: pointer;"
          @click="multiplyHour(hour)">>></button>
        <template v-if="hasResults">
          <span
            :key="`type_res_${hour}`">
            Результат
          </span>
          <span
            :key="`res_void_${hour}`"
            style="grid-column: span 2;"/>
          <span
            :key="`res_sum_vol_${hour}`">
            {{ getSumResVolume(hour) }}
          </span>
          <span
            v-for="section in sections"
            :key="`res_${section}_${hour}`">
          {{ getSectionRes(hour, section) }}
          </span>
        </template>
      </template>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex';
import { isEqual } from 'lodash';

export default {
  name: 'BidEditor',
  props: {
    bid: {
      type: Object,
      default: null,
    },
  },
  data() {
    let i = 0;
    let volumes = [];
    let prices = [];
    if (this.bid) {
      volumes = this.bid.hours.map(({ intervals }) => intervals[0].volume);
      prices = this.bid.hours.map(({ intervals }) => intervals[0].prices.map(d => ({ ...d })));
    }
    return {
      hours: new Array(24).fill().map(() => i++), // eslint-disable-line
      volumes,
      prices,
      invalidVolumes: [],
      invalidPrices: [],
    };
  },
  computed: {
    ...mapState('common', ['username', 'rioEntry', 'adminSession', 'spotResults']),
    ...mapGetters('common', ['selectedSession', 'getNodePrice']),
    title() {
      if (!this.bid) {
        return '❌ заявка не сохранена';
      }
      if (isEqual(this.bid, { _id: this.bid._id, ...this.newBid })
        && isEqual(this.bid.hours.map(({ intervals }) => intervals[0].volume), this.volumes)) {
        return '✅ заявка сохранена';
      }
      return '⚠️ заявка отличается от сохраненной';
    },
    newBid() {
      return {
        trader_code: this.username,
        country_code: this.rioEntry.country_code,
        dir: this.rioEntry.dir,
        session_id: this.selectedSession._id,
        target_date: this.selectedSession.startDate,
        hours: this.volumes.map((volume, hour) => ({
          hour,
          intervals: [{
            interval_num: 0,
            volume,
            prices: this.prices[hour],
          }],
        })),
      };
    },
    sections() {
      const { dir, country_code: countryCode, section_codes: sectionCodes } = this.rioEntry;
      if (dir === 'buy') {
        return ['RUS-ARM', 'RUS-BLR', 'RUS-KAZ', 'KAZ-KGZ']
          .sort((a, b) => !a.includes(countryCode) && b.includes(countryCode));
      }
      return sectionCodes;
    },
    getStyle() {
      // const dif = this.hasResults ? 1 : 0;
      return {
        'grid-template-columns': `repeat(3, 4fr) repeat(${this.sections.length}, 12fr) 1fr`,
      };
    },
    hasResults() {
      return !!this.spotResults;
    },
  },
  methods: {
    bidReady() {
      return this.volumesReady() && this.pricesReady();
    },
    pricesReady() {
      return this.prices.length === 24
        && this.prices.every((prs) => {
          const availSections = prs.map(({ section_code: sc }) => sc);
          return this.rioEntry.section_codes.every(s => availSections.includes(s))
            && prs.every(p => p !== undefined && p !== null);
        })
        && !this.invalidPrices.length;
    },
    volumesReady() {
      return this.volumes.length === 24 && this.volumes.every(v => v !== undefined && v !== null)
        && !this.invalidVolumes.length;
    },
    isInputDisabled(section) {
      return !this.rioEntry.section_codes.includes(section);
    },
    isVolumeValid(hour) {
      return {
        'bid-editor__input_invalid': this.invalidVolumes.includes(hour),
      };
    },
    validateVolume(volume, hour, once = false) {
      if (volume < 0 || Number.isNaN(volume)) {
        if (!this.invalidVolumes.includes(hour)) {
          this.invalidVolumes.push(hour);
        }
      } else {
        const idx = this.invalidVolumes.indexOf(hour);
        this.invalidVolumes = [
          ...this.invalidVolumes.slice(0, idx),
          ...this.invalidVolumes.slice(idx + 1),
        ];
        if (!once && this.prices[hour]) {
          this.prices[hour].forEach(({ section_code: sc, price }) => {
            this.validatePrice(price, hour, sc, true);
          });
        }
      }
    },
    getSumResVolume(hour) {
      return this.bid.hours[hour].intervals[0].prices
        .reduce((prev, { filled_volume: fv }) => prev + fv, 0);
    },
    getVolume(hour) {
      return this.volumes[hour];
    },
    setVolume(hour, { target: { value } }) {
      const volume = parseFloat(value, 10);
      this.$set(this.volumes, hour, volume);
      this.validateVolume(volume, hour);
    },
    isPriceValid(hour, sectionCode) {
      const key = `${hour}${sectionCode}`;
      return {
        'bid-editor__input_invalid': this.invalidPrices.includes(key),
      };
    },
    validatePrice(price, hour, sectionCode, once = false) {
      const volume = this.getVolume(hour);
      const key = `${hour}${sectionCode}`;
      if ((volume === 0 && price !== 0)
        || (volume > 0 && price <= 0)
        || Number.isNaN(price)) {
        if (!this.invalidPrices.includes(key)) {
          this.invalidPrices.push(key);
        }
      } else {
        const idx = this.invalidPrices.indexOf(key);
        if (idx > -1) {
          this.invalidPrices = [
            ...this.invalidPrices.slice(0, idx),
            ...this.invalidPrices.slice(idx + 1),
          ];
        }
        if (!once) {
          this.validateVolume(this.volumes[hour], hour);
        }
      }
    },
    getSectionPrice(hour, sectionCode) {
      const { country_code: countryCode, dir } = this.rioEntry;
      return this.spotResults && this.getNodePrice(hour, countryCode, sectionCode, dir);
    },
    getSectionRes(hour, sectionCode) {
      const pr = this.prices[hour] && this.prices[hour]
        .find(({ section_code: sc }) => sc === sectionCode);
      return pr ? `${pr.filled_volume} x ${this.getSectionPrice(hour, sectionCode)}` : null;
    },
    getPrice(hour, sectionCode) {
      const pr = this.prices[hour] && this.prices[hour]
        .find(({ section_code: sc }) => sc === sectionCode);
      if (pr) return pr.price;
      return null;
    },
    setPrice(hour, sectionCode, { target: { value } }) {
      const price = parseFloat(value, 10);
      if (!this.prices[hour]) {
        this.prices[hour] = [];
      }
      let curPr = this.prices[hour]
        .find(({ section_code: sc }) => sc === sectionCode);
      if (!curPr) {
        curPr = { section_code: sectionCode, price };
        this.prices[hour].push(curPr);
      }
      curPr.price = price;
      this.validatePrice(price, hour, sectionCode);
    },
    multiplyHour(hour) {
      const curVol = this.volumes[hour];
      const curPr = this.prices[hour];
      for (let i = hour + 1; i < 24; i += 1) {
        this.setVolume(i, { target: { value: curVol.toString() } });
        if (curPr) {
          this.prices[i] = [];
          curPr.forEach(({ section_code: sc, price }) => {
            this.setPrice(i, sc, { target: { value: price.toString() } });
          });
        }
      }
    },
    saveBid() {
      this.$socket.sendObj({ type: 'saveBid', msg: { ...this.newBid, ...(this.bid ? { _id: this.bid._id } : {}) } });
    },
    removeBid() {
      this.$socket.sendObj({ type: 'removeBid', msg: this.bid._id });
    },
  },
};
</script>

<style>
.bid-editor {
  display: grid;
}

.bid-editor > * {
  border: 1px solid black;
  padding: 4px;
  text-align: end;
}

.bid-editor__input_invalid {
  background: crimson;
}
</style>
