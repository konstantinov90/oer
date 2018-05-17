<template>
  <div>
    <div
      class="sdd-item"
      @click="onClick">
      <div>
        <span>СД</span>
        <br>
        <span class="sdd-item__info">#{{ sdd._id }}</span>
      </div>
      <div>
        <span>Период договора</span>
        <br>
        <span class="sdd-item__info">{{ contractPeriod }}</span>
      </div>
      <div>
        <span>Покупатель</span>
        <br>
        <span class="sdd-item__info">{{ sdd.buyer }}</span>
      </div>
      <div>
        <span>Продавец</span>
        <br>
        <span class="sdd-item__info">{{ sdd.seller }}</span>
      </div>
      <div>
        <span>Сечение</span>
        <br>
        <span class="sdd-item__info">{{ sdd.section }}</span>
      </div>
      <div>
        <span>Сессия</span>
        <br>
        <span class="sdd-item__info">#{{ sdd.sessionId }}</span>
      </div>
      <div style="width: 250px">
        <span class="sdd-item__info">
          {{ status }}
        </span>
      </div>
    </div>

    <div v-if="!collapsed">
      <sdd-editor :sdd="sdd"/>
    </div>
  </div>
</template>

<script>
import { format } from 'date-fns';
import SddEditor from './SddEditor.vue';

export default {
  name: 'SddView',
  components: {
    SddEditor,
  },
  props: {
    sdd: Object,
    collapsed: Boolean,
    onClick: Function,
  },
  computed: {
    status() {
      const { status } = this.sdd;
      if (status === 'created') return 'Проект';
      if (status === 'negotiation') return 'На согласовании';
      if (status === 'registered') return 'Зарегистрирован';
      if (status === 'rejected') return 'Отклонен';
      return 'Ошибка!';
    },
    contractPeriod() {
      return `${format(new Date(this.sdd.dateStart), 'DD-MM-YYYY')} - ${format(new Date(this.sdd.dateEnd), 'DD-MM-YYYY')}`;
    },
    summary() {
      const sumVol = this.sdd.values.reduce((s, { volume }) => s + volume, 0);
      return `покупатель ${this.sdd.buyer} - ${this.sdd.seller} продавец ${sumVol} МВт ${this.sdd.project ? ' (проект)' : ''}`;
    },
  },
};
</script>

<style>
  .sdd-item {
    cursor: pointer;
    display: flex;
    justify-content: space-around;
    align-items: center;
    border: 1px solid cornflowerblue;
    padding: 5px;
    background: #eee;
    margin: 5px;
  }

  .sdd-item__info {
    color: gray;
  }
</style>
