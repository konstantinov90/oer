<template>
  <div>
    <!-- <span>{{ hasResults }}</span> -->
    <template v-if="!adminSession && !hasResults">
      <button
        :disabled="!bidReady()"
        class="bid-editor__btn bid-editor__btn_save"
        @click="saveBid">
        Сохранить</button>
      <button
        :disabled="!bid"
        class="bid-editor__btn bid-editor__btn_delete"
        @click="removeBid">
        Удалить</button>
    </template>
    <div
      style="display: flex; justify-content: space-between; align-items: center;">
      <h3
        style="display: flex; align-items: center; margin: 0;"
        v-html="title"/>
      <a
        href="#"
        @click="getFile">
        <img
          :src="xlsxImg"
          style="height: 32px;">
      </a>
    </div>
    <div
      :style="getStyle"
      class="bid-editor">
      <span style="grid-row: span 3;">Час</span>
      <span style="grid-row: span 3;">
        <span style="font-size: 25px;">&Sigma;&thinsp;</span> дог
      </span>
      <span style="grid-row: span 3;">Объем</span>
      <span :style="`grid-row: span 2; grid-column: span ${sections.length};`">Цены</span>
      <span
        v-if="!hasResults"
        style="grid-row: span 3;"/>
      <template
        v-if="hasResults">
        <span :style="`grid-column: span ${sections.length * 2 + (rioEntry.dir === 'buy' ? 3 : 2)};`">
          Результаты
        </span>
        <span
          v-for="section in sections"
          :key="`res_${section}`"
          style="grid-column: span 2;">
          {{ section }}
        </span>
        <span :style="`grid-row: span 2;`">Объем</span>
        <span :style="`grid-row: span 2;`">Стоимость</span>
        <span
          v-if="rioEntry.dir === 'buy'"
          :style="`grid-row: span 2;`">
          Стоимость МГП
        </span>
      </template>
      <span
        v-for="section in sections"
        :key="section">
        {{ section }}
      </span>
      <template
        v-if="hasResults">
        <template
          v-for="section in sections">
          <span :key="`head_res_vol_${section}`">Объем</span>
          <span :key="`head_res_price_${section}`">Цена</span>
        </template>
      </template>
      <template v-for="hour in hours">
        <span :key="`hr_${hour}`">{{ hour }}</span>
        <span :key="`sumContr_${hour}`">{{ splitter(getContractsSumVolume(hour)) }}</span>
        <input
          :key="`vol_${hour}`"
          :class="isVolumeValid(hour)"
          :value="splitter(getVolume(hour))"
          :disabled="hasResults"
          @input="setVolume(hour, $event)">
        <input
          v-for="section in sections"
          :key="`${section}_${hour}`"
          :class="isPriceValid(hour, section)"
          :value="splitter(getPrice(hour, section))"
          :disabled="isInputDisabled(section) || hasResults"
          @input="setPrice(hour, section, $event)">
        <button
          v-tooltip.right="'продлить значения до конца'"
          v-if="!hasResults"
          :key="`btn_${hour}`"
          style="cursor: pointer;"
          @click="multiplyHour(hour)">
          <img
            :src="multImg"
            style="transform: scale(0.7);">
        </button>
        <template v-if="hasResults">
          <template
            v-for="section in sections">
            <span
              :key="`res_vol_${section}_${hour}`">
              {{ splitter(getSectionVolume(hour, section)) }}
            </span>
            <span
              :key="`res_pr_${section}_${hour}`">
              {{ splitter(getSectionPrice(hour, section)) }}
            </span>
          </template>
          <span
            :key="`res_sum_vol_${hour}`">
            {{ splitter(getSumResVolume(hour)) }}
          </span>
          <span
            :key="`res_amount_${hour}`">{{ splitter(getAmount(hour)) }}</span>
          <span
            v-if="rioEntry.dir === 'buy'"
            :key="`res_amount_mgp_${hour}`">{{ splitter(getAmountMgp(hour)) }}</span>
        </template>
      </template>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex';
import { isEqual, round } from 'lodash';
import axios from 'axios';
import multImg from '../../../static/mult.svg';
import xlsxImg from '../../../static/xlsx_96x3.png';

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
      xlsxImg,
      multImg,
      hours: new Array(24).fill().map(() => i++), // eslint-disable-line
      volumes,
      prices,
      invalidVolumes: [],
      invalidPrices: [],
    };
  },
  computed: {
    ...mapState('common', ['mgp', 'mgpMatrix', 'rioEntry', 'adminSession', 'spotResults', 'contractsSumVolume']),
    ...mapGetters('common', ['username', 'selectedSession', 'getNodePrice']),
    title() {
      const title = `ценовая заявка на ${this.rioEntry.dir === 'buy' ? 'покупку' : 'продажу'}`;
      if (!this.bid) {
        return `${title} (<span class="sprite sprite__icon sprite__icon_deleted"></span> заявка не сохранена)`;
      }
      if (isEqual(this.bid, { _id: this.bid._id, ...this.newBid })
        && isEqual(this.bid.hours.map(({ intervals }) => intervals[0].volume), this.volumes)) {
        return `${title} (<span class="sprite sprite__icon sprite__icon_ok"></span> заявка сохранена)`;
      }
      return `${title} (<span class="sprite sprite__icon sprite__icon_changed"></span> заявка отличается от сохраненной)`;
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
      if (this.hasResults) {
        return {
          'grid-template-columns': `40px repeat(2, minmax(50px, 100px)) repeat(${this.sections.length * 3}, minmax(60px, 150px)) repeat(${this.rioEntry.dir === 'buy' ? 3 : 2}, minmax(80px, 200px))`,
        };
      }
      return {
        'grid-template-columns': `40px repeat(2, minmax(50px, 100px)) repeat(${this.sections.length}, minmax(100px, 200px)) 33px`,
      };
    },
    hasResults() {
      return !!this.spotResults;
    },
    filelink() {
      return `${IS_PROD ? __webpack_public_path__ : 'http://ats-konstantin1:8080/'}rest/bid_report/?session_id=${this.selectedSession._id}&username=${this.bid.trader_code}`;
    },
  },
  watch: {
    bid() {
      if (this.bid) {
        this.volumes = this.bid.hours.map(({ intervals }) => intervals[0].volume);
        this.prices = this.bid.hours
          .map(({ intervals }) => intervals[0].prices.map(d => ({ ...d })));
      }
    },
  },
  methods: {
    getFile() {
      axios({
        url: this.filelink,
        method: 'GET',
        responseType: 'blob',
      }).then((response) => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `bid_${this.selectedSession._id}_${this.bid.trader_code}.xlsx`);
        document.body.appendChild(link);
        link.click();
      });
    },
    getAmount(hour) {
      return this.sections
        .reduce((s, sec) =>
          (this.getSectionVolume(hour, sec) * this.getSectionPrice(hour, sec)) + s, 0);
    },
    getAmountMgp(hour) {
      const mgpMatrixElement = this.mgpMatrix[this.rioEntry.country_code];
      return Object.entries(mgpMatrixElement).reduce((S, [sectionCode, { mgps }]) =>
        S + (this.getSectionVolume(hour, sectionCode) * mgps.reduce((s, transit) =>
          s + this.getMgpTransitPrice(transit), 0)), 0);
    },
    getContractsSumVolume(hour) {
      if (!this.contractsSumVolume || !this.contractsSumVolume.length) return null;
      return this.contractsSumVolume.find(({ _id }) => _id === hour).vol;
    },
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
    splitter(val) {
      return val.toString().replace(/\B(?=(?:\d{3})+(?!\d))/g, ' ');
    },
    getVolume(hour) {
      return this.volumes[hour];
    },
    setVolume(hour, { target: { value } }) {
      const volume = round(parseFloat(value.toString().replace(/\s/g, ''), 10), 3);
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
    getSectionVolume(hour, sectionCode) {
      const pr = this.prices[hour] && this.prices[hour]
        .find(({ section_code: sc }) => sc === sectionCode);
      return pr ? pr.filled_volume : null;
    },
    getSectionRes(hour, sectionCode) {
      return `${this.getSectionVolume(hour, sectionCode)} x ${this.getSectionPrice(hour, sectionCode)}`;
    },
    getMgpTransitPrice(transit) {
      return this.mgp && this.mgp.sections
        .find(({ section_code }) => section_code === transit).mgp_price;
    },
    getMgpPrice(hour, sectionCode) {
      if (!this.mgp) return null;
      const mgpMatrixElement = this.mgpMatrix[this.rioEntry.country_code][sectionCode];
      if (!mgpMatrixElement) return null;
      const srcPrice = this.getPrice(hour, mgpMatrixElement.src);
      return mgpMatrixElement.mgps.reduce((s, mgpSecCode) => {
        return s - this.getMgpTransitPrice(mgpSecCode);
      }, srcPrice);
    },
    getPrice(hour, sectionCode) {
      const pr = this.prices[hour] && this.prices[hour]
        .find(({ section_code: sc }) => sc === sectionCode);
      if (pr) return pr.price;
      return this.getMgpPrice(hour, sectionCode);
    },
    setPrice(hour, sectionCode, { target: { value } }) {
      const price = round(parseFloat(value.toString().replace(/\s/g, ''), 10), 2);
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
        if (curVol) {
          this.setVolume(i, { target: { value: curVol.toString() } });
        }
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

.bid-editor input {
  width: 100%;
  box-sizing: border-box;
}

.bid-editor > * {
  border: 1px solid black;
  padding: 4px;
  text-align: end;
  display: flex;
  justify-content: center;
  align-items: center;
}

.bid-editor__input_invalid {
  background: crimson;
}

.bid-editor__btn {
  position: absolute;
  right: 0;
  top: 0;
  padding: 15px;
  border-radius: 5px;
  color: white;
}

.bid-editor__btn_save {
  background: #2b7;
  right: 90px;
  font-weight: bold;
}

.bid-editor__btn_save:disabled {
  background: #bbb;
}

.bid-editor__btn_delete {
  background: red;
  padding: 5px;
  top: 10px;
  font-size: 14px;
}
</style>
