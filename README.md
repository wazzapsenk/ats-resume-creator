# ATS Resume Creator

Bir iş ilanına uygun ATS-optimized CV oluşturma ve analiz sistemi.

## Özellikler

- CV analiz ve skoring
- İlan metni ile CV uyum oranı hesaplama
- LaTeX ile dinamik PDF oluşturma
- Anahtar kelime optimizasyonu
- Web tabanlı kullanıcı arayüzü

## Tech Stack

### Backend
- Python + FastAPI
- SQLite
- spaCy/NLTK (NLP)
- LaTeX (PDF oluşturma)

### Frontend
- React + Vite
- Tailwind CSS
- React Hook Form

## Kurulum

### Docker ile (Önerilen)

```bash
cd ats-resume-creator
docker-compose up --build
```

### Manuel Kurulum

#### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Kullanım

1. Browser'da http://localhost:3000 adresine git
2. Kişisel bilgilerini gir
3. İş ilanını yapıştır veya URL ver
4. CV'ni analiz et ve optimize et
5. PDF olarak indir

## API Dokümantasyonu

Backend çalıştıktan sonra: http://localhost:8000/docs

## Proje Yapısı

```
ats-resume-creator/
├── backend/           # FastAPI backend
├── frontend/          # React frontend
├── docker/            # Docker configs
├── latex-templates/   # LaTeX şablonları
├── docs/             # Dokümantasyon
└── uploads/          # Yüklenen dosyalar
```