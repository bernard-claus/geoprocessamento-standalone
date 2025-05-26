import React, { useState } from 'react'

const CheckUpdates = () => {
  const [loading, setLoading] = useState(false)
  const [updateInfo, setUpdateInfo] = useState(null)
  const [error, setError] = useState(null)

  const handleCheck = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setUpdateInfo(null)
    try {
      const result = await window.pywebview.api.check_for_update()
      setUpdateInfo(result)
    } catch (err) {
      setError('Erro ao buscar atualizações.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ position:'absolute', top: 0, left: 0, display: 'flex', alignItems: 'center', gap: 12 }}>
      <span
        onClick={loading ? undefined : handleCheck}
        style={{
          minWidth: 0,
          fontSize: 14,
          borderRadius: 4,
          textDecoration: 'underline',
          cursor: loading ? 'not-allowed' : 'pointer',
          opacity: loading ? 0.7 : 1,
          pointerEvents: loading ? 'none' : 'auto',
          display: 'inline-block',
          userSelect: 'none',
        }}
        role="button"
        tabIndex={0}
      >
        {loading ? 'Verificando...' : 'Verificar atualizações'}
      </span>
      {error && <span style={{ color: 'red', fontSize: 13 }}>{error}</span>}
      {updateInfo && (
        <>
          <span style={{ fontSize: 13, display: 'flex', alignItems: 'center', gap: 4 }}>
            <span>Atual:</span>
            <span>{updateInfo.current_version}</span>
            <span>| Última:</span>
            <span>{updateInfo.latest_version}</span>
          </span>
          {updateInfo.update_available ? (
            <>
              <span style={{ color: 'green', fontWeight: 500, fontSize: 13 }}>Nova versão disponível!</span>
              <a
                href={updateInfo.download_url || updateInfo.release_url}
                target="_blank"
                rel="noopener noreferrer"
                style={{ marginLeft: 8, fontSize: 13, color: '#1976d2', textDecoration: 'underline' }}
              >
                Baixar
              </a>
            </>
          ) : (
            <span style={{ color: '#1976d2', fontSize: 13, fontStyle: 'italic' }}>
              Você já está usando a versão mais recente.
            </span>
          )}
        </>
      )}
    </div>
  )
}

export default CheckUpdates
