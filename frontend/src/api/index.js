import request from '../utils/request'

export const authApi = {
  login: (data) => {
    return request.post('/login', data)
  },
  
  register: (data) => {
    return request.post('/register', data)
  },
  
  getCurrentUser: () => {
    return request.get('/current-user')
  }
}

export const bookApi = {
  getBooks: () => {
    return request.get('/books')
  },
  
  getBook: (id) => {
    return request.get(`/books/${id}`)
  },
  
  createBook: (data) => {
    return request.post('/books', data)
  },
  
  updateBook: (id, data) => {
    return request.put(`/books/${id}`, data)
  },
  
  deleteBook: (id) => {
    return request.delete(`/books/${id}`)
  },
  
  borrowBook: (bookId) => {
    return request.post('/borrow', { book_id: bookId })
  }
}

export const borrowApi = {
  getBorrowRecords: () => {
    return request.get('/borrow-records')
  },
  
  returnBook: (recordId) => {
    return request.post(`/return/${recordId}`)
  }
}

export default {
  authApi,
  bookApi,
  borrowApi
}
