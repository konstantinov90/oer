<template>
  <div>
    <button @click="closeSession">Закрыть сессию</button>
    <a
      href="#"
      @click="getFile">
      Получить МДП, полученные в сессии СД #{{ selectedSession.sd_session_id }}
    </a>
    <div class="container">
      <!--UPLOAD-->
      <form enctype="multipart/form-data" novalidate v-if="isInitial || isSaving">
        <h1>Upload images</h1>
        <div class="dropbox">
          <input type="file" multiple name="file" :disabled="isSaving" @change="filesChange($event.target.name, $event.target.files); fileCount = $event.target.files.length" accept="image/*" class="input-file">
          <p v-if="isInitial">
            Drag your file(s) here to begin<br> or click to browse
          </p>
          <p v-if="isSaving">
            Uploading {{ fileCount }} files...
          </p>
        </div>
      </form>
  </div>
  </div>
</template>

<script>
import axios from 'axios';
import { mapGetters } from 'vuex';

const STATUS_INITIAL = 0, STATUS_SAVING = 1, STATUS_SUCCESS = 2, STATUS_FAILED = 3;

export default {
  name: 'FuturesPhaseView',
  data() {
    return {
      uploadedFiles: [],
      uploadError: null,
      currentStatus: null,
    };
  },
  computed: {
    ...mapGetters('common', ['selectedSession']),
    isInitial() {
      return this.currentStatus === STATUS_INITIAL;
    },
    isSaving() {
      return this.currentStatus === STATUS_SAVING;
    },
    isSuccess() {
      return this.currentStatus === STATUS_SUCCESS;
    },
    isFailed() {
      return this.currentStatus === STATUS_FAILED;
    },
    filelink() {
      return `${IS_PROD ? __webpack_public_path__ : 'http://ats-konstantin1:8080/'}rest/sdd_section_limits/?sd_session_id=${this.selectedSession.sd_session_id}`;
    },
  },
  methods: {
    getFile() {
      axios({
        url: this.filelink,
        method: 'GET',
        responseType: 'blob',
      }).then((response) => {
        const filename = response.headers['content-disposition'].split('=')[1].replace(/"/g, '');
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
      });
    },
    closeSession() {
      this.$socket.sendObj({ type: 'futuresCloseSession', msg: this.selectedSession._id });
    },
    reset() {
      // reset form to initial state
      this.currentStatus = STATUS_INITIAL;
      this.uploadedFiles = [];
      this.uploadError = null;
    },
    save(formData) {
      // upload data to the server
      this.currentStatus = STATUS_SAVING;

      axios.post(`${IS_PROD ? __webpack_public_path__ : 'http://ats-konstantin1:8080/'}rest/upload_file/?session_id=${this.selectedSession._id}`, formData)
        .then(({ data }) => {
          this.uploadedFiles = [].concat(data);
          this.currentStatus = STATUS_SUCCESS;
        })
        .catch(({ response }) => {
          this.uploadError = response;
          this.currentStatus = STATUS_FAILED;
        });
    },
    filesChange(fieldName, fileList) {
      // handle file changes
      const formData = new FormData();

      if (!fileList.length) return;

      // append the files to FormData
      Array
        .from(Array(fileList.length).keys())
        .map((x) => {
          formData.append(fieldName, fileList[x], fileList[x].name);
        });

      // save it
      this.save(formData);
    },
  },
  mounted() {
    this.reset();
  },
};
</script>

<style>
.dropbox {
    outline: 2px dashed grey; /* the dash box */
    outline-offset: -10px;
    background: lightcyan;
    color: dimgray;
    padding: 10px 10px;
    min-height: 200px; /* minimum height */
    position: relative;
    cursor: pointer;
  }

  .input-file {
    opacity: 0; /* invisible but it's there! */
    width: 100%;
    height: 200px;
    position: absolute;
    cursor: pointer;
  }

  .dropbox:hover {
    background: lightblue; /* when mouse over to the drop zone, change color */
  }

  .dropbox p {
    font-size: 1.2em;
    text-align: center;
    padding: 50px 0;
  }
</style>
