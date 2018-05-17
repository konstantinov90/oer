<template>
  <div
    :class="editorClass">
    <editor
      ref="editor"
      :value="bidText"
      class="bid-editor"
      lang="json"
      theme="textmate"
      width="100%"
      height="500"
      @init="editorInit"
      @input="editorInput"/>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex';
import Editor from 'vue2-ace-editor';
import Ajv from 'ajv';

const ajv = new Ajv({ useDefaults: 'shared' });


export default {
  name: 'BidEditor',
  components: {
    Editor,
  },
  props: {
    editableUser: {
      type: String,
      required: true,
    },
    msgType: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      content: '',
      editorInvalid: false,
    };
  },
  computed: {
    ...mapState('common', [
      'phase',
      'rioEntry',
      'username',
    ]),
    ...mapGetters('common', [
      'bidText',
      'dateFormatted',
    ]),
    jsonSchema() {
      const { country_code, dir, section_codes } = this.rioEntry; // eslint-disable-line
      return {
        type: 'object',
        required: ['_id', 'hours', 'country_code', 'dir'],
        additionalProperties: false,
        properties: {
          _id: { type: 'string', const: this.editableUser },
          country_code: { type: 'string', const: country_code },
          dir: { type: 'string', const: dir },
          target_date: { type: 'string', const: this.dateFormatted },
          hours: {
            type: 'array',
            minItems: 24,
            maxItems: 24,
            items: {
              type: 'object',
              required: ['hour', 'intervals'],
              additionalProperties: false,
              properties: {
                hour: { type: 'number', minimum: 0, maximum: 23 },
                intervals: {
                  type: 'array',
                  minItems: 1,
                  maxItems: 3,
                  items: {
                    type: 'object',
                    required: ['volume', 'prices'],
                    additionalProperties: false,
                    properties: {
                      volume: { type: 'number', maximum: 1e6 },
                      prices: {
                        type: 'array',
                        minItems: section_codes.length,
                        maxItems: section_codes.length,
                        items: {
                          type: 'object',
                          required: ['section_code', 'price'],
                          additionalProperties: false,
                          properties: {
                            section_code: { type: 'string', pattern: section_codes.map(sc => `(${sc})`).join('|') },
                            price: { type: 'number', maximum: 1e5 },
                          },
                        },
                      },
                    },
                  },
                },
              },
            },
          },
        },
      };
    },
    validator() {
      return ajv.compile(this.jsonSchema);
    },
    editorClass() {
      return {
        'bid-editor-invalid': this.editorInvalid,
        'bid-editor-disabled': this.phase === 'bids-accepted' && this.username !== 'admin',
      };
    },
  },
  created() {
    this.$socket.sendObj({ type: this.msgType, msg: this.editableUser });
    this.$store.watch(() => this.phase, this.forceUpdate);
  },
  methods: {
    forceUpdate(phase) {
      if (phase === 'bids-accepted' && this.$refs.editor) {
        this.$refs.editor.editor.session.setValue(this.bidText);
      }
    },
    editorInit() {
      // language extension prerequsite...
      /* eslint-disable */
      require('brace/ext/language_tools');
      require('brace/mode/json');
      require('brace/theme/textmate');
      /* eslint-enable */
    },
    editorInput(input) {
      if (input === this.bidText && !this.editorInvalid) {
        console.log('skip');
        return;
      }
      let obj;
      try {
        obj = JSON.parse(input);
      } catch (e) {
        return;
      }

      /* eslint-disable no-underscore-dangle */
      // obj._id = this.username;
      // obj.country = this.rioEntry.country;
      // obj.type = this.rioEntry.type;
      /* eslint-enable no-underscore-dangle */

      this.editorInvalid = !this.validator(obj);
      if (!this.editorInvalid) {
        this.$socket.sendObj({ type: 'bid', msg: JSON.stringify(obj) });
      } else {
        console.log(ajv.errors);
      }
    },
  },
};
</script>

<style lang="stylus">
.bid-editor-invalid .ace_editor
  background #d74747
.bid-editor-disabled .ace_editor
  pointer-events none
  opacity 0.5
.bid-editor
  border-radius 10px
  & *
    font-family 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace
</style>
