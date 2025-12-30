from django.core.management.base import BaseCommand

from core.services import load_excel_data


class Command(BaseCommand):
    help = "Carga datos del Excel y calcula posiciones iniciales e históricas"

    def add_arguments(self, parser):
        parser.add_argument(
            'excel_path',
            type=str,
            help='Ruta al archivo datos.xlsx'
        )

    def handle(self, *args, **options):
        excel_path = options['excel_path']
        
        self.stdout.write("Leyendo archivo Excel...")
        
        with open(excel_path, 'rb') as f:
            load_excel_data(f)
        
        self.stdout.write(self.style.SUCCESS("ETL completado exitosamente"))
