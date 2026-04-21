import axios from 'axios'

const baseURL = 'http://127.0.0.1:5000/api'

const request = axios.create({
  baseURL,
  timeout: 10000
})

// 登录接口
export function login(data) {
  return request.post('/login', data)
}

// LLM 生成绘本
export function generateStory(topic) {
  return request.post('/llm/generate', { topic })
}

// 保存草稿
export function saveDraft(data) {
  return request.post('/story/save', data)
}

// 提交审核
export function submitReview(data) {
  return request.post('/story/save', data)
}

// 获取我的作品
export function getMyStories(author) {
  return request.post('/story/my', { author })
}

// 获取已发布绘本
export function getPublished() {
  return request.get('/books/list')
}

// 审核通过
export function approveStory(id) {
  return request.post('/book/audit', { id })
}

export default request