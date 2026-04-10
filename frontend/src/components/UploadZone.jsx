import { useState, useRef } from 'react'

export default function UploadZone({ onFileSelected, isProcessing, onLoadDemo, progressMessage }) {
  const [isDragOver, setIsDragOver] = useState(false)
  const fileInputRef = useRef(null)

  function handleDragOver(e) {
    e.preventDefault()
    setIsDragOver(true)
  }

  function handleDragLeave() {
    setIsDragOver(false)
  }

  function handleDrop(e) {
    e.preventDefault()
    setIsDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) onFileSelected(file)
  }

  function handleClick() {
    fileInputRef.current?.click()
  }

  function handleFileChange(e) {
    const file = e.target.files[0]
    if (file) onFileSelected(file)
  }

  return (
    <section className="w-full">
      <div className="relative group">
        <div className="absolute -inset-1 bg-gradient-to-r from-primary/10 to-secondary/10 rounded-xl blur opacity-25 group-hover:opacity-50 transition duration-1000"></div>
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleClick}
          className={`relative border-2 border-dashed rounded-xl p-12 text-center transition-all cursor-pointer ${
            isDragOver
              ? 'border-primary/60 bg-primary-fixed/20'
              : 'border-outline/30 bg-surface-container-low hover:bg-surface-container-high'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.jpg,.jpeg,.png"
            onChange={handleFileChange}
            className="hidden"
          />
          <div className="flex flex-col items-center justify-center space-y-4">
            <div className="w-16 h-16 rounded-full bg-primary-fixed flex items-center justify-center text-on-primary-fixed">
              <span className="material-symbols-outlined text-3xl">
                {isProcessing ? 'hourglass_empty' : 'upload_file'}
              </span>
            </div>
            <div>
              <h3 className="text-xl font-semibold text-on-surface">
                {isProcessing ? 'Processing document...' : 'Upload statement or receipt'}
              </h3>
              <p className="text-on-surface-variant text-sm mt-1">
                {isProcessing
                  ? (progressMessage || 'Parsing with AI — this may take a few seconds')
                  : 'Drag and drop your PDF statement or receipt image here to start parsing'}
              </p>
            </div>
            {!isProcessing && (
              <div className="flex items-center gap-4">
                <button className="cta-gradient px-8 py-3 rounded-full text-on-primary font-medium shadow-lg hover:opacity-90 active:scale-95 transition-all">
                  Select Files
                </button>
                {onLoadDemo && (
                  <button
                    onClick={(e) => { e.stopPropagation(); onLoadDemo(); }}
                    className="px-6 py-3 rounded-full border-2 border-primary/30 text-primary font-medium hover:bg-primary-fixed/20 active:scale-95 transition-all"
                  >
                    Try Demo
                  </button>
                )}
              </div>
            )}
            {isProcessing && (
              <div className="w-8 h-8 border-4 border-primary/30 border-t-primary rounded-full animate-spin"></div>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}
