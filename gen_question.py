import openai
import time
import json
import os
import time
from datetime import datetime

from pandas import Timestamp

class QuestionGenerator:
    def __init__(self, model_name="speakleash/Bielik-11B-v2.3-Instruct"):
        self.client = openai.OpenAI(
            base_url="http://10.3.9.3:8001/v1",
            api_key="vLLM",
        )
        self.model_name = model_name
        self.output_dir= r"C:\Users\jszuran\Desktop\question_json"
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_questions(self, chunk_text: str, num_questions: int = 3):
        """
        Generuje pytania kontrolne dla podanego tekstu chunka.
        """
        try:
            start_time = time.time()
            completion = self.client.chat.completions.create(
                model=self.model_name,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": """Jesteś ekspertem w analizie i kategoryzacji zapytań dotyczących oprogramowania medycznego. 
                    Zawsze odpowiadaj w formacie JSON.
                    JSON ma mieć dokładnie takie pola:
                    {
                      "questions": ["pytanie1", "pytanie2", "pytanie3"]
                    }

                ZASADY ANALIZY:
                1. Zawsze identyfikuj dokładnie 3-5 głównych tematów
                2. Tematy muszą być w mianowniku (forma podstawowa)
                3. Używaj tylko słów kluczowych z dziedziny medycznej/IT
                4. Priorityzuj tematy według ważności (od najważniejszego)
                5. Unikaj duplikatów i synonimów
                6. Używaj standardowych terminów z przykładów

                WYMAGANY FORMAT ODPOWIEDZI:
                Tematy: [temat1], [temat2], [temat3], [temat4], [temat5]

                DOZWOLONE KATEGORIE TEMATÓW:
                - Operacje: dodawanie, usuwanie, edycja, kopiowanie, modyfikacja, skanowanie
                - Obiekty medyczne: pacjent, badanie, skierowanie, e-skierowanie, zlecenie, rozpoznanie, wizyta
                - Dokumenty: dokument przychodu, rejestr pacjentów, zlecenie badania
                - Techniczne: kod kreskowy, interfejs użytkownika, walidacja, komunikaty systemowe
                - Problemy: błąd, obsługa błędów, operacja nieudana, widoczność pola"""},
                   
                    {"role": "user", "content": f"""Przeanalizuj to zapytanie według podanych zasad i wybierz dokładnie 3-5 tematów z dozwolonych kategorii:

                PRZYKŁADY DO NAŚLADOWANIA:

                Zapytanie: "Jak system reaguje na sczytanie kodu kreskowego towaru, który nie jest jeszcze na dokumencie przychodu?"
                Tematy: skanowanie kodu kreskowego, dokument przychodu, walidacja, obsługa błędów

                Zapytanie: "Jak dodać zlecenie na badanie dla pacjenta w trakcie wizyty?"
                Tematy: dodawanie zlecenia badania, pacjent, wizyta, zarządzanie badaniami

                Zapytanie: "Pole do wprowadzenia numeru e-skierowania w oknie rezerwacji terminu jest niewidoczne."
                Tematy: e-skierowanie, rezerwacja terminu, interfejs użytkownika, widoczność pola

                Zapytanie: "Jak skopiować dane skierowania od innego pacjenta lub z poprzedniej wizyty?"
                Tematy: kopiowanie danych, skierowanie, pacjent, wizyta

                Zapytanie: "Próbuję usunąć pacjenta z rejestru, ale operacja się nie udaje. Dlaczego?"
                Tematy: usuwanie pacjenta, rejestr pacjentów, operacja nieudana, błąd

                Zapytanie: "Czy mogę zmienić zlecone badanie, np. z morfologii na badanie moczu, już po jego zleceniu?"
                Tematy: modyfikacja zlecenia, badanie, edycja zlecenia, pacjent

                Zapytanie: "Podczas odmowy przyjęcia pacjenta pojawia się komunikat o braku rozpoznania. Co należy zrobić?"
                Tematy: odmowa przyjęcia pacjenta, rozpoznanie, komunikaty systemowe, obsługa błędów

                ZAPYTANIE DO ANALIZY: "{chunk_text}"
                Na podstawie powyższych zasad, stwórz 3 pytania i zwróć je w formacie JSON:

                Odpowiedź (używaj dokładnie tego formatu):"""}
                ],
            )
            end_time = time.time()
            duration = end_time - start_time

            response_content = completion.choices[0].message.content
            try:
                parsed = json.loads(response_content)
                questions = parsed.get("questions", [])
            except Exception:
                # jeśli model nie zwróci czystego JSON, bierzemy raw text
                questions = [response_content]
            # Tutaj zamiast tylko tematów możesz później poprosić model o generowanie pytań
            return {
                "content": chunk_text,
                "questions": [response_content],
                "duration": duration
            }

        except Exception as e:
            print(f" Błąd podczas generowania pytań: {e}")
            return {"content": chunk_text, "questions": [], "duration": 0.0}
    
    def save_to_json(self, results, source_file: str):
        try:
            base_name = os.path.splitext(os.path.basename(source_file))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_path = os.path.join(self.output_dir, f"{base_name}_{timestamp}_questions.json")

            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"Zapisano w {out_path}")
        except Exception as e:
            print(f" Błąd zapisu do JSON: {e}")
