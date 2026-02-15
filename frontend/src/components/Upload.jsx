import React, { useState, useCallback, useRef } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload as UploadIcon, FileText, X, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { scanConfiguration } from '../utils/api'

const Upload = ({ setScanData, isScanning, setIsScanning, setActiveTab }) => {
  const [files, setFiles] = useState({})
  const [error, setError] = useState('')
  const [mode, setMode] = useState('devops')
  const fileInputs = useRef({})

  const handleFileSelect = useCallback((event, fileKey) => {
    const selectedFiles = event.target.files
    if (selectedFiles && selectedFiles.length > 0) {
      processFile(selectedFiles[0], fileKey)
    }
  }, [])

  const processFile = useCallback((file, fileKey) => {
    console.log('Processing file:', file.name, file.type, file.size)
    
    const reader = new FileReader()
    
    reader.onload = () => {
      try {
        console.log('File read successfully, content length:', reader.result.length)
        setFiles(prev => ({
          ...prev,
          [fileKey]: {
            file: file,
            content: reader.result,
            name: file.name
          }
        }))
        setError('')
        console.log('File state updated successfully')
      } catch (error) {
        console.error('File processing error:', error)
        setError(`Failed to process file: ${error.message}`)
      }
    }
    
    reader.onerror = () => {
      console.error('FileReader error')
      setError('Failed to read file')
    }
    
    reader.readAsText(file)
  }, [])

  const onDrop = useCallback((acceptedFiles, fileKey) => {
    console.log('onDrop called with:', acceptedFiles, 'for fileKey:', fileKey)
    
    if (acceptedFiles.length === 0) {
      setError('No valid files selected')
      return
    }

    processFile(acceptedFiles[0], fileKey)
  }, [processFile])

  const getDropzoneProps = (fileKey, accept) => {
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
      onDrop: (acceptedFiles) => onDrop(acceptedFiles, fileKey),
      accept,
      multiple: false,
      maxFiles: 1,
      noClick: false,
      noKeyboard: false,
      onError: (error) => {
        console.error('Dropzone error:', error)
        setError(`File upload error: ${error.message}`)
      }
    })

    return { getRootProps, getInputProps, isDragActive }
  }

  const dockerfileProps = getDropzoneProps('dockerfile', {
    'text/plain': ['.dockerfile'],
    'application/octet-stream': ['.dockerfile'],
    'text/x-dockerfile': ['.dockerfile'],
    'application/x-dockerfile': ['.dockerfile']
  })

  const composeProps = getDropzoneProps('docker_compose', {
    'application/x-yaml': ['.yml', '.yaml'],
    'text/yaml': ['.yml', '.yaml'],
    'text/x-yaml': ['.yml', '.yaml'],
    'application/yaml': ['.yml', '.yaml']
  })

  const envProps = getDropzoneProps('env_file', {
    'text/plain': ['.env'],
    'application/x-env': ['.env'],
    'application/octet-stream': ['.env']
  })

  const removeFile = (fileKey) => {
    setFiles(prev => {
      const newFiles = { ...prev }
      delete newFiles[fileKey]
      return newFiles
    })
  }

  const handleScan = async () => {
    if (Object.keys(files).length === 0) {
      setError('Please upload at least one configuration file')
      return
    }

    setIsScanning(true)
    setError('')

    try {
      const formData = new FormData()
      
      if (files.dockerfile) {
        formData.append('dockerfile', files.dockerfile.file)
      }
      if (files.docker_compose) {
        formData.append('docker_compose', files.docker_compose.file)
      }
      if (files.env_file) {
        formData.append('env_file', files.env_file.file)
      }
      
      formData.append('mode', mode)

      const result = await scanConfiguration(formData)
      setScanData(result)
      setActiveTab('dashboard')
    } catch (err) {
      setError(err.message || 'Scan failed. Please try again.')
    } finally {
      setIsScanning(false)
    }
  }

  const FileUploadArea = ({ fileKey, title, description, icon: Icon, props, file }) => (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-300">{title}</label>
      {!file ? (
        <div className="space-y-2">
          <div
            {...props.getRootProps()}
            className={`border-2 border-dashed rounded-lg p-6 cursor-pointer transition-colors ${
              props.isDragActive
                ? 'border-primary-500 bg-primary-500/10'
                : 'border-gray-600 hover:border-gray-500'
            }`}
          >
            <input {...props.getInputProps()} />
            <div className="flex flex-col items-center gap-2 text-center">
              <Icon className="w-8 h-8 text-gray-400" />
              <div>
                <p className="text-sm text-gray-300">
                  {props.isDragActive ? 'Drop file here' : description}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Click to browse or drag and drop
                </p>
              </div>
            </div>
          </div>
          
          {/* Fallback file input */}
          <div className="flex items-center gap-2">
            <input
              ref={(el) => fileInputs.current[fileKey] = el}
              type="file"
              onChange={(e) => handleFileSelect(e, fileKey)}
              className="hidden"
              accept={getAcceptString(fileKey)}
            />
            <button
              onClick={() => fileInputs.current[fileKey]?.click()}
              className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-lg text-sm transition-colors"
            >
              Or choose file manually
            </button>
          </div>
        </div>
      ) : (
        <div className="flex items-center gap-3 p-3 bg-gray-800 rounded-lg border border-gray-700">
          <FileText className="w-5 h-5 text-primary-400" />
          <span className="flex-1 text-sm text-gray-300">{file.name}</span>
          <button
            onClick={() => removeFile(fileKey)}
            className="text-gray-400 hover:text-error-400 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  )

  const getAcceptString = (fileKey) => {
    switch (fileKey) {
      case 'dockerfile':
        return '.dockerfile,Dockerfile'
      case 'docker_compose':
        return '.yml,.yaml'
      case 'env_file':
        return '.env'
      default:
        return '*'
    }
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Upload Configuration Files</h1>
        <p className="text-gray-400">
          Upload your Dockerfile, docker-compose.yml, and .env files for AI-powered security analysis
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-error-500/10 border border-error-500/30 rounded-lg flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-error-400" />
          <span className="text-error-400">{error}</span>
        </div>
      )}

      <div className="space-y-6">
        <div className="card">
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Analysis Mode
            </label>
            <div className="flex gap-4">
              <button
                onClick={() => setMode('beginner')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  mode === 'beginner'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                Beginner
              </button>
              <button
                onClick={() => setMode('devops')}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  mode === 'devops'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                }`}
              >
                DevOps
              </button>
            </div>
            <p className="mt-2 text-sm text-gray-400">
              {mode === 'beginner' 
                ? 'Simple explanations for beginners learning DevOps'
                : 'Technical analysis for experienced DevOps engineers'
              }
            </p>
          </div>

          <div className="grid gap-6">
            <FileUploadArea
              fileKey="dockerfile"
              title="Dockerfile"
              description="Drag & drop your Dockerfile or click to browse"
              icon={FileText}
              props={dockerfileProps}
              file={files.dockerfile}
            />

            <FileUploadArea
              fileKey="docker_compose"
              title="Docker Compose"
              description="Drag & drop your docker-compose.yml or click to browse"
              icon={FileText}
              props={composeProps}
              file={files.docker_compose}
            />

            <FileUploadArea
              fileKey="env_file"
              title="Environment File"
              description="Drag & drop your .env file or click to browse (optional)"
              icon={FileText}
              props={envProps}
              file={files.env_file}
            />
          </div>

          <div className="mt-8 flex justify-center">
            <button
              onClick={handleScan}
              disabled={Object.keys(files).length === 0}
              className="btn-primary flex items-center gap-2 px-8 py-3 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isScanning ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Scanning...
                </>
              ) : (
                <>
                  <UploadIcon className="w-5 h-5" />
                  Start Analysis
                </>
              )}
            </button>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-white mb-4">What We Analyze</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-success-400" />
              <span className="text-gray-300">Security vulnerabilities</span>
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-success-400" />
              <span className="text-gray-300">Best practices violations</span>
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-success-400" />
              <span className="text-gray-300">Configuration conflicts</span>
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-success-400" />
              <span className="text-gray-300">Secret leakage detection</span>
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-success-400" />
              <span className="text-gray-300">Dependency analysis</span>
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-success-400" />
              <span className="text-gray-300">Deployment risk scoring</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Upload
