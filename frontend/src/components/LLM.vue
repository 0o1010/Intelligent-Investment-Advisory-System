<template>
    <div>
        <div style="margin-bottom: 5px">

            <el-select v-model="model" filterable placeholder="Select a model" class="model-select"
                       style="margin-left: 5px; margin-bottom: 10px" @change="onModelChange">
                <el-option
                    v-for="item in models"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value">
                </el-option>
            </el-select>
            <div class="chat-container">
                <div class="chat-box" ref="chatBox">
                    <div
                        v-for="(msg, index) in messages"
                        :key="index"
                        :class="['chat-message', msg.role]"
                    >
                        <p><strong>{{ msg.role === 'user' ? 'You' : 'Assistant (' + model + ')' }}:</strong>
                        </p>

                        <template v-if="msg.role === 'assistant'">
                            <div v-if="extractThink(msg.text)">
                                <el-button
                                    type="text"
                                    size="mini"
                                    @click="msg.showThink = !msg.showThink"
                                >
                                    {{ msg.showThink ? 'Hide thoughts' : 'Show thoughts' }}
                                </el-button>

                                <el-card
                                    v-if="msg.showThink"
                                    class="think-block"
                                    shadow="never"
                                >
                                    <template #header>
                                        <span style="font-size: 13px; color: #999;">Assistant is thinking...</span>
                                    </template>
                                    <div style="font-size: 13px;" v-html="marked(extractThink(msg.text))"/>
                                </el-card>
                            </div>

                            <div class="markdown-body" v-html="marked(stripThink(msg.text))"/>
                        </template>

                        <p v-else>{{ msg.text }}</p>
                    </div>

                </div>

                <div class="chat-input-bar">

                    <el-input
                        v-model="userInput"
                        type="textarea"
                        :autosize="{ minRows: 4, maxRows: 10 }"
                        placeholder="Please input your question here..."
                        class="input-area"
                        @keydown.enter.native.prevent="sendMessage"
                    />

                    <el-button type="primary" icon="el-icon-s-promotion" @click="sendMessage">
                        Send
                    </el-button>
                </div>
            </div>
        </div>


    </div>
</template>

<script>
import {marked} from 'marked';

export default {
    name: "LLM",
    data() {
        return {
            userInput: '',
            messages: [],
            model: '',
            models: [
                {
                    value: 'Meta-Llama-3.1-405B-Instruct',
                    label: 'Meta-Llama-3.1-405B-Instruct'
                }, {
                    value: 'Qwen3-32B',
                    label: 'Qwen3-32B'
                }, {
                    value: 'DeepSeek-R1-0528',
                    label: 'DeepSeek-R1-0528'
                },
            ]
        }
    },

    methods: {
        marked,
        loadGet() {
            this.$nextTick(this.scrollToBottom);
            this.$axios.get(this.$httpUrl + '/load', {
                params: {
                    username: sessionStorage.getItem('user'),
                    model: this.model
                }
            }).then(res => res.data).then(res => {
                this.messages = [];
                console.log(res)
                if (res.code === 200) {
                    console.log(res.data)
                    for (let i = 0; i < res.data.length; i++) {
                        this.messages.push({role: 'user', text: res.data[i]['user']});
                        this.messages.push({role: 'assistant', text: res.data[i]['assistant'], showThink: false});
                    }
                } else {
                    this.messages.push({role: 'assistant', text: 'Error: ' + res.data});
                }
                this.$nextTick(this.scrollToBottom);
            }).catch(() => {
                this.messages.pop();
                this.messages.push({role: 'assistant', text: 'Request failed'});
                this.$nextTick(this.scrollToBottom);
            });
        },
        sendMessage() {
            if (!this.model || !this.userInput.trim()) {
                this.$message.warning("Please select a model and input your question.");
                return;
            }

            const input = this.userInput.trim();

            this.messages.push({role: 'user', text: input});
            this.userInput = '';

            this.$nextTick(this.scrollToBottom);

            this.messages.push({role: 'assistant', text: 'Thinking...'});

            this.$axios.get(this.$httpUrl + '/suggest', {
                params: {
                    model: this.model,
                    message: input,
                    username: sessionStorage.getItem('user')
                }
            }).then(res => res.data).then(res => {
                this.messages.pop();
                console.log(res)
                if (res.code === 200) {
                    this.messages.push({role: 'assistant', text: res.data, showThink: false});
                } else {
                    this.messages.push({role: 'assistant', text: 'Error: ' + res.data});
                }
                this.$nextTick(this.scrollToBottom);
            }).catch(() => {
                this.messages.pop();
                this.messages.push({role: 'assistant', text: 'Request failed'});
                this.$nextTick(this.scrollToBottom);
            });
        },
        scrollToBottom() {
            const chat = this.$refs.chatBox;
            chat.scrollTop = chat.scrollHeight;
        },
        extractThink(text) {
            const match = text.match(/<think>([\s\S]*?)<\/think>/);
            return match ? match[1].trim() : null;
        },

        stripThink(text) {
            return text.replace(/<think>[\s\S]*?<\/think>/g, '').trim();
        },
        onModelChange() {
            this.messages = [];
            setTimeout(() => {
                this.loadGet();
            }, 100);
        }
    },
}
</script>

<style scoped>
.chat-container {
    display: flex;
    flex-direction: column;
    height: 80vh;
    background-color: #f9f9f9;
}

.chat-box {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    background: #fff;
    margin: 10px;
    border-radius: 10px;
    border: 1px solid #ddd;
}

.chat-message {
    margin-bottom: 15px;
    line-height: 1.5;
}

.chat-message.user {
    text-align: right;
    color: #409EFF;
}

.chat-message.assistant {
    text-align: left;
    color: #606266;
}

.chat-input-bar {
    display: flex;
    align-items: center;
    padding: 10px;
    background: #fafafa;
    border-top: 1px solid #ddd;
}

.model-select {
    width: 220px;
    margin-right: 10px;
}

.input-area {
    flex: 1;
    margin-right: 10px;
}

.markdown-body {
    font-size: 15px;
    line-height: 1.6;
    color: #333;
    word-break: break-word;
}

.think-block {
    background-color: #f6f6f6;
    margin-bottom: 10px;
    border: 1px dashed #d3d3d3;
    font-family: 'Courier New', monospace;
}

</style>
