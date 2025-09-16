# ATS Resume Creator - Kurulum ve Test Rehberi

## Gerekli Yazılımlar

### 1. Python (Backend için)
```bash
# Python 3.8+ gerekli
python --version
```

### 2. Node.js (Frontend için)
```bash
# Node.js 16+ gerekli
node --version
npm --version
```

### 3. LaTeX (PDF generation için)
**Windows:**
- [MiKTeX](https://miktex.org/download) indir ve kur
- Veya [TeX Live](https://tug.org/texlive/windows.html) kullan

**macOS:**
```bash
brew install --cask mactex
```

**Ubuntu/Debian:**
```bash
sudo apt-get install texlive-full
```

### 4. Git
```bash
git --version
```

## Kurulum Adımları

### 1. Repository'yi Clone Et
```bash
cd D:\GithubRepositories\ATS_ResumeCreator
# Eğer henüz clone etmediysen:
# git clone <repository-url> ats-resume-creator
cd ats-resume-creator
```

### 2. Backend Kurulumu
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Frontend Kurulumu
```bash
cd ../frontend
npm install
```

### 4. Veritabanı Kurulumu
```bash
cd ../backend
# Virtual environment aktif olmalı
python -m alembic upgrade head
```

## Programı Çalıştırma

### 1. Backend'i Başlat
```bash
cd backend
# Virtual environment aktif olmalı
uvicorn app.main:app --reload --port 8000
```
Backend: http://localhost:8000

### 2. Frontend'i Başlat (Yeni terminal)
```bash
cd frontend
npm run dev
```
Frontend: http://localhost:3000

## Test Etme

### 1. Temel Fonksiyonlar
1. http://localhost:3000 adresine git
2. Hesap oluştur (Register)
3. Giriş yap (Login)
4. Dashboard'u görüntüle

### 2. Resume Oluştur
1. "New Resume" butonuna tıkla
2. Resume bilgilerini doldur
3. Kaydet

### 3. Job Posting Ekle
1. "Add Job Posting" butonuna tıkla
2. İş ilanı bilgilerini doldur
3. Kaydet

### 4. Analiz Yap
1. "Start Analysis" butonuna tıkla
2. Resume ve Job Posting seç
3. Analizi başlat
4. Sonuçları görüntüle

### 5. PDF Oluştur
1. Dashboard'da resume yanındaki PDF butonuna tıkla
2. Template seç
3. Preview veya Download

## LaTeX Test Etme
```bash
# LaTeX kurulumunu test et
pdflatex --version

# Backend'de LaTeX testi
curl http://localhost:8000/api/pdf/validate
```

## API Testleri
```bash
# API durumunu kontrol et
curl http://localhost:8000/health

# Template listesini al
curl http://localhost:8000/api/pdf/templates
```

## Sorun Giderme

### LaTeX Sorunları
- MiKTeX/TeX Live düzgün kurulu mu?
- PATH değişkeninde pdflatex var mı?
- Windows'ta admin yetkisiyle kurulum yaptın mı?

### Backend Sorunları
- Virtual environment aktif mi?
- Requirements.txt kuruldu mu?
- Port 8000 boş mu?

### Frontend Sorunları
- Node.js 16+ kurulu mu?
- npm install başarılı mı?
- Port 3000 boş mu?

### Database Sorunları
- Alembic migration çalıştı mı?
- SQLite dosyası oluştu mu?

## Test Data
İlk test için örnek data:

**Test Resume:**
- Ad: John Doe
- Email: john@example.com
- Pozisyon: Software Developer
- Deneyim: Python, React, FastAPI

**Test Job Posting:**
- Pozisyon: Full Stack Developer
- Şirket: Tech Company
- Gereksinimler: Python, React, API development