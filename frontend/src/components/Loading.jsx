export function Loading() {
  return (
    <div className="loading">
      <span className="spinner"></span> Loading...
    </div>
  )
}

export function Error({ message }) {
  return (
    <div className="error">
      Error: {message}
    </div>
  )
}
