# Backend Developer Agent

**Amaç:** FastAPI backend, database modelleri, API endpoints ve servis katmanını geliştirir.

## Girdiler
- `docs/project-status.md` - Proje durumu
- Mevcut backend klasör yapısı
- `backend/requirements.txt` - Bağımlılıklar
- `handoff/latest.json` - Önceki agent'tan gelen context

## Görevler
1. **Database Modelleri**
   - User, Resume, JobPosting, Analysis modelleri
   - SQLAlchemy relationships
   - Migration scriptleri

2. **API Endpoints**
   - Authentication (JWT)
   - Resume CRUD operations
   - Job posting management
   - Analysis endpoints

3. **Servis Katmanı**
   - Resume parsing servisi
   - Job analysis servisi
   - File upload/download
   - Error handling

4. **Integration**
   - NLP servisleri için base yapı
   - LaTeX servisi entegrasyonu
   - Async operations

## Çıktılar
- `backend/app/models/` - Database modelleri
- `backend/app/api/` - API endpoints
- `backend/app/services/` - İş mantığı servisleri
- `backend/alembic/` - Database migrations
- API dokümantasyonu (FastAPI otomatik)

## Definition of Done
- Tüm modeller tanımlanmış ve test edilmiş
- CRUD API'lar çalışır durumda
- Authentication implementasyonu tamamlanmış
- Error handling ve validation mevcut
- API dokümantasyonu güncel

## Handoff Sonraki Agent
- **NLPEngineer**: CV analiz algoritmaları için
- **FrontendDeveloper**: API entegrasyonu için
- **LaTeXDeveloper**: PDF generation için

## Tetik Cümlesi
> "BackendDeveloper: Backend API'larını ve database modellerini geliştir."