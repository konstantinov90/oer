<template>
  <div
    ref="self"
    class="sdd-editor">
    <span
      style="display: flex; align-items: center;"
      v-html="title"/>
    <template v-if="!adminSession">
      <template v-if="isNew">
        <button
          :disabled="!sddProj"
          class="sdd-editor__button sdd-editor__button_offer"
          @click="offer">
          Сохранить и отправить контрагенту
        </button>
        <button
          :disabled="!sddProj"
          class="sdd-editor__button sdd-editor__button_save"
          @click="save">
          Сохранить без отправки контрагенту
        </button>
        <button
          v-if="!sdd"
          class="sdd-editor__button sdd-editor__button_cancel"
          @click="cancel">
          Отмена
        </button>
      </template>
      <template v-if="underReview">
        <template v-if="isChanged">
          <button
            :disabled="!sddProj"
            class="sdd-editor__button sdd-editor__button_offer"
            @click="reoffer">
            Отправить на согласование контрагенту
          </button>
        </template>
        <template v-if="!isChanged">
          <button
            class="sdd-editor__button sdd-editor__button_offer"
            @click="confirm">
            Подтвердить и зарегистрировать
          </button>
          <button
            class="sdd-editor__button sdd-editor__button_decline"
            @click="decline">
            Отказ в регистрации
          </button>
        </template>
      </template>
      <template v-if="awaitingReview">
        <button
          disabled
          class="sdd-editor__button sdd-editor__button_offer">
          Ожидайте решения контрагента
        </button>
      </template>
      <template v-if="isRejected">
        <button
          class="sdd-editor__button sdd-editor__button_save"
          @click="change">
          Изменить
        </button>
      </template>
    </template>
    <h2>Свободный договор:</h2>
    <div class="picker-wrapper">
      <label>{{ !adminSession && rioEntry.dir === 'sell' ? 'Продавец' : 'Покупатель' }}:</label>
      <input
        :value="!adminSession ? username : sdd.buyer"
        type="text"
        disabled>
    </div>
    <div style="display: flex; align-items: center;">
      <div class="picker-wrapper" style="width: 500px;">
        <label>{{ !adminSession ? contragentType : 'Продавец' }}:</label>
        <multiselect
          :value="selectedContragent"
          :options="possibleContragents"
          :placeholder="'выберите'"
          :allow-empty="false"
          :disabled="!!sdd"
          select-label=""
          selected-label=""
          deselect-label=""
          class="sdd-editor__multiselect-wrapper"
          @select="onSelectContragent">
          <template
            slot="option"
            slot-scope="props">
            <div
              v-tooltip.right="{
                boundariesElement: 'body',
                content: props.option.name,
                delay: 0,
              }"
              style="padding: 12px; margin: -12px">
              {{ props.option._id }}
            </div>
          </template>
          <template
            slot="singleLabel"
            slot-scope="props">
            <span>{{ props.option._id }}</span>
          </template>
        </multiselect>
      </div>
      <div class="tooltip">
        <span
          v-if="selectedContragent"
          class="tooltip-inner">
          {{ selectedContragent.name }}
        </span>
      </div>
    </div>
    <div
      v-if="selectedContragent"
      class="picker-wrapper">
      <label>Сечение поставки:</label>
      <input
        :value="selectedSection"
        disabled>
        <!-- <select
        :disabled="inputDisabled"
        @input="onSelectSection">
        <option
          :selected="true"
          disabled
          value>
          {{ inputDisabled ? sdd.section : ' -- выберите -- ' }}
        </option>
        <option
          v-for="sec in possibleSections[possibleSectionKey]"
          :key="sec"
          :selected="selectedSection === sec"
          :value="sec">
          {{ sec }}
        </option>
      </select> -->
    </div>
    <div class="picker-wrapper picker-wrapper_dates">
      <label>Период поставки:</label>
      <label>с</label>
      <date-selector
        :value="selectedDateStart"
        :prev-date="selectedDateStart"
        :on-select="onSelectDateStart"
        :from-date="selectedSession.startDate"
        :to-date="selectedSession.finishDate"/>
      <template v-if="selectedDateStart">
        <label>по</label>
        <date-selector
          :value="selectedDateEnd"
          :prev-date="selectedDateStart"
          :on-select="onSelectDateEnd"
          :from-date="selectedSession.startDate"
          :to-date="selectedSession.finishDate"/>
      </template>
    </div>
    <div
      v-if="hours.length">
      <h3>График поставки по СД:</h3>
    </div>
    <div
      v-if="hours.length"
      :style="{
        'grid-template-columns': `repeat(2, 4fr) repeat(${hasResults ? '3' : '2'}, 12fr)${inputDisabled ? '' : ' 1fr'}`
      }"
      class="graph-grid">
      <p>Дата</p>
      <p>Час</p>
      <p>Объем</p>
      <p v-if="hasResults">Принятый объем</p>
      <p>Цена</p>
      <span
        v-if="!inputDisabled"
        style="border: none;"
      />
      <template
        v-for="hour in hours">
        <label :key="`dt_${hour}`">{{ getDate(parseInt(hour/24, 10)) }}</label>
        <label :key="`hr_${hour}`">{{ hour % 24 }}</label>
        <input
          :key="`vol_${hour}`"
          :disabled="inputDisabled"
          :value="splitter(sddProjValues[hour].volume)"
          @input="changeValue('volume', hour, $event)">
        <span
          v-if="hasResults"
          :key="`acc_${hour}`">
          {{ sdd.values[hour].accepted_volume }}
        </span>
        <input
          :key="`pr_${hour}`"
          :disabled="inputDisabled"
          :value="splitter(sddProjValues[hour].price)"
          @input="changeValue('price', hour, $event)" >
        <span
          v-tooltip.right="'продлить значения до конца'"
          v-if="!inputDisabled"
          :key="hour"
          style="cursor: pointer;"
          @click="multiplyHour(hour)">
          <img
            :src="multImg"
            style="transform: scale(0.7);">
        </span>
      </template>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex';
import { addDays, compareAsc, differenceInDays, format } from 'date-fns';
import { isEqual, round } from 'lodash';
import Multiselect from 'vue-multiselect';
// import Datepicker from 'vuejs-datepicker';
import DateSelector from './DateSelector.vue';
import multImg from '../../../static/mult.svg';

const {
  c: CREATED,
  n: NEGOTIATION,
  r: REGISTERED,
  j: REJECTED,
} = {
  c: 'created',
  n: 'negotiation',
  r: 'registered',
  j: 'rejected',
};

export default {
  name: 'SddEditor',
  components: {
    DateSelector,
    Multiselect,
  },
  props: {
    closeFn: {
      type: Function,
      required: false,
      default: () => {},
    },
    sdd: {
      type: Object,
      required: false,
      default: null,
    },
    tooltipVisible: {
      type: Boolean,
      default: true,
    },
  },
  data() {
    let sddProjValues = [];
    let selectedContragent;
    let selectedSection;
    let selectedDateStart;
    let selectedDateEnd;

    if (this.sdd) {
      sddProjValues = this.sdd.values.map(d => ({ ...d }));
      selectedContragent = this.sdd.author === this.sdd.buyer ? this.sdd.seller : this.sdd.buyer;
      selectedDateStart = new Date(this.sdd.dateStart);
      selectedDateEnd = new Date(this.sdd.dateEnd);
      selectedSection = this.sdd.section;
    }

    return {
      multImg,
      sddProjValues,
      selectedContragent,
      selectedSection,
      selectedDateStart,
      selectedDateEnd,
      possibleSections: {
        // 'ARM-BLR': ['RUS-ARM', 'RUS-BLR'],
        // 'ARM-RUS': ['RUS-ARM'],
        // 'ARM-KAZ': ['RUS-ARM', 'RUS-KAZ'],
        // 'ARM-KGZ': ['RUS-ARM', 'RUS-KAZ', 'KAZ-KGZ'],
        // 'BLR-ARM': ['RUS-BLR', 'RUS-ARM'],
        // 'BLR-RUS': ['RUS-BLR'],
        // 'BLR-KAZ': ['RUS-BLR', 'RUS-KAZ'],
        // 'BLR-KGZ': ['RUS-BLR', 'RUS-KAZ', 'KAZ-KGZ'],
        // 'RUS-ARM': ['RUS-ARM'],
        // 'RUS-BLR': ['RUS-BLR'],
        // 'RUS-KAZ': ['RUS-KAZ'],
        // 'RUS-KGZ': ['RUS-KAZ', 'KAZ-KGZ'],
        // 'KAZ-ARM': ['RUS-KAZ', 'RUS-ARM'],
        // 'KAZ-BLR': ['RUS-KAZ', 'RUS-BLR'],
        // 'KAZ-RUS': ['RUS-KAZ'],
        // 'KAZ-KGZ': ['KAZ-KGZ'],
        // 'KGZ-ARM': ['KAZ-KGZ', 'RUS-KAZ', 'RUS-ARM'],
        // 'KGZ-BLR': ['KAZ-KGZ', 'RUS-KAZ', 'RUS-BLR'],
        // 'KGZ-RUS': ['KAZ-KGZ', 'RUS-KAZ'],
        // 'KGZ-KAZ': ['KAZ-KGZ'],
        'ARM-BLR': 'RUS-ARM',
        'ARM-RUS': 'RUS-ARM',
        'ARM-KAZ': 'RUS-ARM',
        'ARM-KGZ': 'RUS-ARM',
        'BLR-ARM': 'RUS-BLR',
        'BLR-RUS': 'RUS-BLR',
        'BLR-KAZ': 'RUS-BLR',
        'BLR-KGZ': 'RUS-BLR',
        'RUS-ARM': 'RUS-ARM',
        'RUS-BLR': 'RUS-BLR',
        'RUS-KAZ': 'RUS-KAZ',
        'RUS-KGZ': 'RUS-KAZ',
        'KAZ-ARM': 'RUS-KAZ',
        'KAZ-BLR': 'RUS-KAZ',
        'KAZ-RUS': 'RUS-KAZ',
        'KAZ-KGZ': 'KAZ-KGZ',
        'KGZ-ARM': 'KAZ-KGZ',
        'KGZ-BLR': 'KAZ-KGZ',
        'KGZ-RUS': 'KAZ-KGZ',
        'KGZ-KAZ': 'KAZ-KGZ',
      },
    };
  },
  computed: {
    ...mapState('common', ['rioEntry', 'adminSession']),
    ...mapState('client', ['possibleContragents']),
    ...mapGetters('common', ['username', 'selectedSession']),
    hasResults() {
      return this.selectedSession.status === 'closed' && this.sdd.values[0].accepted_volume !== undefined;
    },
    openDate() {
      return this.selectedSession.startDate;
    },
    dif() {
      if (!this.selectedDateStart || !this.selectedDateEnd) {
        return 0;
      }

      return differenceInDays(this.selectedDateEnd, this.selectedDateStart) + 1;
    },
    hours() {
      let hour = 0;
      return new Array(this.dif * 24).fill().map(() => hour++) // eslint-disable-line
    },
    contragentType() {
      return this.rioEntry && this.rioEntry.dir === 'buy' ? 'Продавец' : 'Покупатель';
    },
    possibleSectionKey() {
      // return this.adminSession ? this.sdd.section : `${this.rioEntry.country_code}-${this.selectedContragent.country_code}`;
      const countries = [this.rioEntry.country_code, this.selectedContragent.country_code];
      if (this.rioEntry.dir === 'buy') {
        countries.reverse();
      }
      return this.adminSession ? this.sdd.section : countries.join('-');
    },
    sddProj() {
      if (!this.selectedDateStart || !this.selectedDateEnd
        || !this.selectedContragent || !this.selectedSection
        || this.sddProjValues.some(({ volume, price }) => !volume || !price)) {
        return null;
      }

      return {
        sessionId: this.sdd ? this.sdd.sessionId : this.selectedSession._id,
        dateStart: this.selectedDateStart,
        dateEnd: this.selectedDateEnd,
        author: this.sdd ? this.sdd.author : this.username,
        reviewer: this.sdd ? this.sdd.reviewer : this.selectedContragent._id,
        buyer: this.rioEntry && this.rioEntry.dir === 'buy' ? this.username : this.selectedContragent._id,
        seller: this.rioEntry && this.rioEntry.dir === 'sell' ? this.username : this.selectedContragent._id,
        section: this.selectedSection,
        values: this.sddProjValues,
      };
    },
    inputDisabled() {
      if (this.adminSession) return true;
      if (!this.sdd) return false;
      if (this.sdd.status === NEGOTIATION) {
        if (this.sdd.reviewer === this.username) {
          return false;
        }
        return true;
      }
      if (this.sdd.status === CREATED) return false;
      if (this.sdd.status === REJECTED || this.sdd.status === REGISTERED) return true;
      return true;
    },
    isNew() {
      return !this.sdd || this.sdd.status === CREATED;
    },
    underReview() {
      return this.sdd && this.sdd.status === NEGOTIATION && this.sdd.reviewer === this.username;
    },
    awaitingReview() {
      return this.sdd && this.sdd.status === NEGOTIATION && this.sdd.reviewer !== this.username;
    },
    isRejected() {
      return this.sdd && this.sdd.status === REJECTED;
    },
    isChanged() {
      return this.sdd && !isEqual(this.sdd, this.prepareSdd(this.sdd.status));
    },
    title() {
      if (!this.sdd) {
        return '';
      }
      if (!this.isChanged) {
        return '<span class="sprite sprite__icon sprite__icon_ok"></span> договор сохранен';
      }
      return '<span class="sprite sprite__icon sprite__icon_changed"></span> договор отличается от сохраненного';
    },
  },
  watch: {
    sdd() {
      if (this.sdd) {
        this.sddProjValues = this.sdd.values.map(d => ({ ...d }));
        this.selectedDateStart = new Date(this.sdd.dateStart);
        this.selectedDateEnd = new Date(this.sdd.dateEnd);
        this.selectedSection = this.sdd.section;

        this.elaborateSddContragent();
      }
    },
  },
  created() {
    this.elaborateSddContragent();
    window.addEventListener('keydown', this.processKeyDown);
  },
  destroyed() {
    window.removeEventListener('keydown', this.processKeyDown);
  },
  methods: {
    splitter(val) {
      if (val === undefined || val === null) return null;
      return val.toString().replace(/\B(?=(?:\d{3})+(?!\d))/g, ' ');
    },
    elaborateSddContragent() {
      if (this.sdd) {
        let contrId;
        if (this.sdd.author === this.username) {
          contrId = this.sdd.author === this.sdd.buyer ? this.sdd.seller : this.sdd.buyer;
        } else {
          contrId = this.sdd.author;
        }
        this.selectedContragent = this.possibleContragents
          .find(({ _id }) => _id === contrId);
      }
    },
    processKeyDown({ key }) {
      if (key === 'Escape') {
        this.closeFn();
      }
    },
    getDate(idx) {
      return format(addDays(this.selectedDateStart, idx), 'DD.MM.YYYY');
    },
    changeValue(valueType, hour, { target }) {
      let dim;
      switch (valueType) {
        case 'price':
          dim = 2;
          break;
        case 'volume':
          dim = 3;
          break;
        default:
          throw new Error('invalid valueType!');
      }
      const value = round(parseFloat(target.value.replace(',', '.').replace(' ', ''), 10), dim);
      this.sddProjValues[hour][valueType] = value;
    },
    onSelectDateStart(selectedDate) {
      this.selectedDateStart = selectedDate;
      if (!this.selectedDateEnd || compareAsc(this.selectedDateStart, this.selectedDateEnd) > 0) {
        this.onSelectDateEnd(this.selectedDateStart);
      } else {
        this.updateSddProjValues();
      }
    },
    onSelectDateEnd(selectedDate) {
      this.selectedDateEnd = selectedDate;
      this.updateSddProjValues();
    },
    updateSddProjValues() {
      if (!this.selectedDateStart || !this.selectedDateEnd) {
        return;
      }
      for (let i = 0; i < this.sddProjValues.length; i += 1) {
        this.sddProjValues[i].tdate = addDays(this.selectedDateStart, parseInt(i / 24, 10));
      }
      for (let i = this.sddProjValues.length; i < this.dif * 24; i += 1) {
        const tdate = addDays(this.selectedDateStart, parseInt(i / 24, 10));
        this.sddProjValues.push({
          volume: null,
          price: null,
          hour: i % 24,
          tdate,
        });
      }
      this.sddProjValues = this.sddProjValues.slice(0, this.dif * 24);
    },
    onSelectContragent(value) {
      this.selectedContragent = value;
      // if (!this.possibleSections[this.possibleSectionKey].includes(this.selectedSection)) {
      //   this.selectedSection = null;
      // }
      this.selectedSection = this.possibleSections[this.possibleSectionKey];
    },
    // onSelectSection({ target: { value } }) {
    //   this.selectedSection = value;
    // },
    multiplyHour(thour) {
      const curHour = this.sddProjValues[thour];
      this.sddProjValues = [
        ...this.sddProjValues.slice(0, thour).map(d => ({ ...d })),
        ...this.sddProjValues.slice(thour).map(({ hour, tdate }) => ({ ...curHour, hour, tdate })),
      ];
    },
    cancel() {
      this.closeFn();
    },
    prepareSdd(status) {
      const sdd = { ...this.sddProj, status };
      if (this.sdd) {
        sdd._id = this.sdd._id;
      }
      return sdd;
    },
    reoffer() {
      const sdd = this.prepareSdd(NEGOTIATION);
      sdd.reviewer = this.selectedContragent._id;
      this.$socket.sendObj({ type: 'sdd', msg: sdd });
      this.closeFn();
    },
    offer() {
      this.$socket.sendObj({ type: 'sdd', msg: this.prepareSdd(NEGOTIATION) });
      if (!this.sdd) {
        this.closeFn();
      }
    },
    save() {
      this.change();
      if (!this.sdd) {
        this.closeFn();
      }
    },
    confirm() {
      this.$socket.sendObj({ type: 'sdd', msg: this.prepareSdd(REGISTERED) });
    },
    decline() {
      this.$socket.sendObj({ type: 'sdd', msg: this.prepareSdd(REJECTED) });
    },
    change() {
      this.$socket.sendObj({ type: 'sdd', msg: this.prepareSdd(CREATED) });
    },
  },
};
</script>

<style>

.picker-wrapper {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  max-width: 500px;
  border: 1px solid black;
  border-radius: 5px;
  margin: 2px;
  align-items: center;
}

.picker-wrapper input,
.picker-wrapper select {
  width: 150px;
  box-sizing: border-box;
  border-radius: 5px;
}

.picker-wrapper_dates {
  justify-content: end;
}

.picker-wrapper_dates label:not(:first-child) {
  margin: 0 5px;
}

.picker-wrapper_dates label:first-child {
  flex: 1;
}

.graph-grid {
  display: grid;
  max-width: 1000px;
}

.graph-grid > * {
  border: 1px solid black;
  padding: 4px;
  text-align: end;
  display: flex;
  justify-content: center;
  align-items: center;
}

.graph-grid > p {
  background: #bbb;

}

.sdd-editor {
  position: relative;
}

.sdd-editor__button {
  position: absolute;
  border-radius: 15px;
  max-width: 200px;
  top: 0;
}

.sdd-editor__button_offer {
  background: #2b7;
  padding: 5px;
  right: 0;
  color: #fff;
  font-weight: bold;
}

.sdd-editor__button_save {
  background: #ab0;
  padding: 5px;
  right: 0;
  top: 60px;
  color: #fff;
  font-weight: bold;
}

.sdd-editor__button:disabled {
  background: #bbb;
}

.sdd-editor__button_cancel {
  padding: 10px;
  right: 25px;
  top: 120px;
}

.sdd-editor__button_decline {
  background: red;
  color: #fff;
  font-size: 14px;
  padding: 5px;
  top: 70px;
  right: 25px
}

.sdd-editor__multiselect-wrapper {
  width: 50%;
}
</style>

