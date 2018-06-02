<template>
  <div
    class="sdd-item__wrapper">
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
      <div
        style="
          width: 250px;
          display: flex;
          justify-content: space-between;
          align-items: center;
        ">
        <span class="sdd-item__info">
          {{ status }}
        </span>
        <img
          v-if="sdd.status === 'created' && sdd.author === username"
          :src="deleteImg"
          class="sdd-item__delete-img"
          @click.stop="deleteSdd(sdd._id)">
      </div>
    </div>

    <div
      :class="{'sdd-editor__wrapper_collapsed': collapsed}"
      class="sdd-editor__wrapper">
      <sdd-editor :sdd="sdd"/>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
import { format } from 'date-fns';
import SddEditor from './SddEditor.vue';
import deleteImg from '../../../static/delete.svg';

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
  data() {
    return {
      deleteImg,
      dateFmt: 'DD.MM.YYYY',
    };
  },
  computed: {
    ...mapGetters('common', ['username']),
    status() {
      const { status, reviewer } = this.sdd;
      if (status === 'created') return 'Проект';
      if (status === 'negotiation') {
        if (reviewer === this.username) return 'Требуется согласование';
        return 'Ожидается согласование контрагента';
      }
      if (status === 'registered') return 'Зарегистрирован';
      if (status === 'rejected') return 'Отклонен';
      return 'Ошибка!';
    },
    contractPeriod() {
      return `${format(new Date(this.sdd.dateStart), this.dateFmt)} - ${format(new Date(this.sdd.dateEnd), this.dateFmt)}`;
    },
    summary() {
      const sumVol = this.sdd.values.reduce((s, { volume }) => s + volume, 0);
      return `покупатель ${this.sdd.buyer} - ${this.sdd.seller} продавец ${sumVol} МВт ${this.sdd.project ? ' (проект)' : ''}`;
    },
  },
  methods: {
    deleteSdd(sddId) {
      if (confirm(`Вы уверены, что хотите удалить договор # ${sddId}?`)) {
        this.$socket.sendObj({ type: 'deleteSdd', msg: sddId });
      }
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
    padding: 5px;
    background: #eee;
  }
  .sdd-item__wrapper {
    border: 1px solid cornflowerblue;
    margin: 5px;
  }

  .sdd-item__info {
    color: gray;
  }

  .sdd-item__delete-img {
    height: 28px;
  }

  .sdd-item__delete-img:hover {
    background: #ccc;
    box-sizing: border-box;
    border-radius: 4px;
  }

  .sdd-editor__wrapper {
    transition: max-height 300ms linear, transform 300ms linear;
    overflow-y: auto;
    max-height: 800px;
    transform: rotateX(0);
  }

  .sdd-editor__wrapper_collapsed {
    max-height: 0px;
    transform: rotateX(90deg);
  }
</style>
