import { useState } from 'react'

export default function CommandCard({
  title,
  method,
  description,
  inputs = [],
  onExecute
}) {
  const [values, setValues] = useState({})
  const [response, setResponse] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleChange = (name, value) => {
    setValues(prev => ({ ...prev, [name]: value }))
  }

  const handleExecute = async () => {
    setLoading(true)
    setError(null)
    setResponse(null)

    // Merge user values with defaults from inputs
    const mergedValues = {}
    inputs.forEach(input => {
      if (values[input.name] !== undefined) {
        mergedValues[input.name] = values[input.name]
      } else if (input.type === 'select' && input.options?.length > 0) {
        mergedValues[input.name] = input.options[0].value
      } else {
        mergedValues[input.name] = input.defaultValue || ''
      }
    })

    try {
      const result = await onExecute(mergedValues)
      setResponse(result.data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  const methodClass = `method-${method.toLowerCase()}`
  const btnClass = `btn btn-${method.toLowerCase()}`

  return (
    <div className="command-card">
      <div className="command-header">
        <h4 className="command-title">{title}</h4>
        <span className={`method-badge ${methodClass}`}>{method}</span>
      </div>
      
      {description && (
        <p className="command-desc">{description}</p>
      )}

      {inputs.length > 0 && (
        <div className="command-inputs">
          {inputs.map((input) => (
            input.type === 'select' ? (
              <select
                key={input.name}
                className="input"
                value={values[input.name] || input.defaultValue || (input.options?.[0]?.value) || ''}
                onChange={(e) => handleChange(input.name, e.target.value)}
              >
                {input.options.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            ) : input.type === 'textarea' ? (
              <textarea
                key={input.name}
                className="input"
                placeholder={input.placeholder}
                value={values[input.name] || ''}
                onChange={(e) => handleChange(input.name, e.target.value)}
                rows={input.rows || 2}
              />
            ) : (
              <input
                key={input.name}
                type={input.type || 'text'}
                className="input"
                placeholder={input.placeholder}
                value={values[input.name] || input.defaultValue || ''}
                onChange={(e) => handleChange(input.name, e.target.value)}
              />
            )
          ))}
        </div>
      )}

      <button
        className={btnClass}
        onClick={handleExecute}
        disabled={loading}
        style={{ width: '100%' }}
      >
        {loading ? 'Executing...' : 'Execute'}
      </button>

      {(response !== null || error) && (
        <div className={`command-response ${error ? 'response-error' : 'response-success'}`}>
          <pre>{error ? `Error: ${JSON.stringify(error, null, 2)}` : JSON.stringify(response, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}
