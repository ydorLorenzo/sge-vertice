from adm.models import *
from django.urls import reverse


# Create your models here.
class Actividad(models.Model):
    descripcion = models.CharField(max_length=60, verbose_name='Usuario', blank=True, null=True)

    def __str__(self):
        return self.descripcion


class Trabajador(models.Model):
    # Datos personales del trabajador
    primer_nombre = models.CharField(max_length=20, verbose_name='Primer nombre')
    segundo_nombre = models.CharField(max_length=20, blank=True, verbose_name='Segundo nombre')
    apellidos = models.CharField(max_length=60, verbose_name='Apellidos')
    ci = models.CharField(max_length=11, verbose_name='Carnet de Identidad', unique=True)
    foto = models.ImageField(upload_to='fotos', verbose_name='Foto', blank=True)
    SEXO_OPT = (('M', 'Masculino'), ('F', 'Femenino'))
    sexo = models.CharField(max_length=1, choices=SEXO_OPT, verbose_name='Sexo', default=SEXO_OPT[0])
    ETNIA_OPT = (('B', 'Blanca'), ('M', 'Mestiza'), ('N', 'Negra'))
    motivo_alta = models.CharField(max_length=60, verbose_name='Motivo Alta', default="Ocupar plaza vacante",
                                   blank=True, null=True)
    etnia = models.CharField(max_length=10, choices=ETNIA_OPT, verbose_name='Etnia', default=ETNIA_OPT[0])
    lugar_nacimiento = models.CharField(max_length=30, verbose_name='Lugar de nacimiento', blank=True)
    estatura = models.FloatField(max_length=3, verbose_name='Estatura (M)', blank=True, null=True)
    peso = models.FloatField(max_length=3, verbose_name='Peso (K)', blank=True, null=True)
    nombre_madre = models.CharField(max_length=40, verbose_name='Nombre de la madre', blank=True)
    nombre_padre = models.CharField(max_length=40, verbose_name='Nombre del padre', blank=True)
    ESTADO_OPT = (
        ('Soltero', 'Soltero(a)'), ('Casado', 'Casado(a)'), ('Divorciado', 'Divorciado(a)'), ('Viudo', 'Viudo(a)'))
    estado_civil = models.CharField(max_length=10, choices=ESTADO_OPT, verbose_name='Estado civil',
                                    default=ESTADO_OPT[0])
    hijos = models.PositiveIntegerField(verbose_name='Cantidad de hijos', default=0)
    LICENCIA_OPT = (('0', 'Primera'), ('1', 'Segunda'), ('2', 'Tercera'), ('3', 'Cuarta'), ('4', 'Quinta'))
    licencia = models.CharField(max_length=20, blank=True, verbose_name='Licencia de conducción', choices=LICENCIA_OPT,
                                default='No procede')
    enfermedades = models.CharField(max_length=100, verbose_name='Enfermedades que padece', default='Ninguna',
                                    blank=True)
    direccion = models.CharField(max_length=500, verbose_name='Dirección')
    telefono = models.CharField(max_length=8, verbose_name='Teléfono', blank=True)
    fecha_nac = models.DateField(verbose_name="Fecha de nacimiento", editable=False, null=True, blank=True)
    org_plantilla = models.PositiveIntegerField(verbose_name='Organización en la plantilla')
    unidad_org = models.ForeignKey(UnidadOrg, on_delete=models.DO_NOTHING, verbose_name='Unidad organizacional')
    departamento = models.ForeignKey(Departamento, on_delete=models.DO_NOTHING, verbose_name='Departamento')
    cargo = models.ForeignKey(Cargo, on_delete=models.DO_NOTHING, verbose_name='Cargo')
    codigo_interno = models.CharField(max_length=3, unique=True, verbose_name='Código Interno')
    usuario = models.CharField(max_length=20, verbose_name='Usuario', blank=True, null=True, default='Ninguno')
    residencia = models.CharField(max_length=20, verbose_name='Municipio de residencia')
    # Datos laborales y salariales
    CATEGORIA_OPT = (('A', 'Administrativo'), ('C', 'Cuadro '), ('O', 'Operario'), ('S', 'Servicio'),
                     ('T', 'Técnico '))
    categoria = models.CharField(choices=CATEGORIA_OPT, max_length=15, verbose_name='Categoría ocupacional')
    PLANTILLA_OPT = (('A', 'Administrativo'), ('P', 'Productivo'))
    t_plantilla = models.CharField(choices=PLANTILLA_OPT, max_length=15, verbose_name='Tipo de plantilla', blank=True)
    CONTRATO_OPT = (
        ('1', 'Nombramiento'), ('2', 'Indeterminado'), ('3', 'Determinado'), ('4', 'Adiestramiento'),
        ('5', 'Disponible'),
        ('6', 'A prueba'))
    t_contrato = models.CharField(choices=CONTRATO_OPT, max_length=20, verbose_name='Tipo de contrato')
    FUERZA_I_OPT = (('1', 'Otras Empresas'), ('2', 'Reclusos'), ('3', 'Microbrigrada'), ('4', 'Otros'))
    fuerza_i = models.CharField(choices=FUERZA_I_OPT, max_length=20, verbose_name='Fuerza irregular', blank=True)
    T_PAGO_OPT = (('S', 'Sueldista'), ('V', 'Vinculado'))
    t_pago = models.CharField(choices=T_PAGO_OPT, max_length=20, verbose_name='Tipo de pago')
    S_PAGO_OPT = (('1', 'Res. 6 2016'), ('2', 'Res.1 2017'), ('3', 'Res.15 2016'))
    s_pago = models.CharField(choices=S_PAGO_OPT, max_length=20, verbose_name='Sistema de pago')
    j_laboral = models.BooleanField(verbose_name='Jornada Laboral de 208 horas', default=False)
    escala_salarial = models.ForeignKey(EscalaSalarial, on_delete=models.DO_NOTHING)
    salario_escala = models.DecimalField(verbose_name='Salario escala', max_digits=5, decimal_places=2, default=0.00)
    incre_res = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Pago por perfeccionamiento')
    sal_bas = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Salario básico')
    POR_CIES_OPT = (('0', '0%'), ('1', '30%'), ('2', '50%'))
    por_cies = models.CharField(max_length=3, choices=POR_CIES_OPT, verbose_name='% CIES', default=POR_CIES_OPT[0])
    cies = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='CIES')
    sal_plus = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Salario plus', default=0.00)
    sal_cond_anor = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Salario condiciones anormales',
                                        default=0.00)
    POR_ANTI_OPT = (('0', '0%'), ('1', '5%'), ('2', '10%'))
    por_anti = models.CharField(choices=POR_ANTI_OPT, max_length=3, verbose_name="% Antiguedad",
                                default=POR_ANTI_OPT[0])
    antiguedad = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    fecha_contrato = models.DateField(verbose_name="Fecha de contrato")
    fecha_alta = models.DateField(verbose_name="Fecha de alta al cargo")
    fecha_disponible = models.DateField(blank=True, verbose_name="Fecha de inicio disponibilidad", null=True)
    fecha_ingreso = models.DateField(verbose_name="Fecha de ingreso al organismo")
    albergado = models.BooleanField()
    sancionado = models.BooleanField()
    CAT_CIENT_OPT = (('1', 'Ninguna'), ('2', 'Máster'), ('3', 'Doctor'))
    cat_cient = models.CharField(max_length=10, choices=CAT_CIENT_OPT)
    sal_cat_cient = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Salario x cat. científica",
                                        blank=True, null=True, default=0.00)
    salario_total = models.DecimalField(max_digits=7, verbose_name='Salario Total', blank=True, null=True,
                                        decimal_places=2)
    salario_jornada_laboral = models.DecimalField(max_digits=5, verbose_name='Salario por Jornada Laboral', blank=True,
                                                  null=True, default=0.00, decimal_places=2)
    # Datos docentes
    actividad = models.ForeignKey(Actividad, on_delete=models.DO_NOTHING, verbose_name="Actividad", blank=True,
                                  null=True)
    calificacion = models.ForeignKey(Calificacion, on_delete=models.DO_NOTHING, verbose_name="Calificación", blank=True,
                                     null=True)
    especialidad = models.ForeignKey(Especialidad, on_delete=models.DO_NOTHING, verbose_name="Especialidad", blank=True,
                                     null=True)
    anno_graduado = models.PositiveIntegerField(verbose_name="Año de graduado", blank=True, null=True)
    centro_graduacion = models.CharField(max_length=40, verbose_name="Centro de graduación", default='Ninguno')
    pais_graduacion = models.CharField(max_length=20, verbose_name="País de graduación", default='Ninguno')
    ESCOLARIDAD_OPT = (
        ('6to', '6to Grado'), ('9no ', '9no Grado'), ('12mo ', '12mo Grado'), ('TM', 'Técnico Medio'),
        ('OC', 'Obrero Calificado'),
        ('Univ', 'Universitario'))
    escolaridad = models.CharField(max_length=20, choices=ESCOLARIDAD_OPT, verbose_name="Escolaridad")
    idioma = models.CharField(max_length=20, verbose_name="Idioma", blank=True, null=True, default='Ninguno')
    TIPO_TEC = (
        ('TA', 'Tec. Administrativo'), ('TD ', 'Tec.Dirigente'), ('TP ', 'Tec. Plaza Profesional'),
        ('TN', 'Tec. No Titulado'), ('TU', 'Tec. Universitario'),
        ('TM', 'Tec. Medio'), ('Nin', 'Ninguno'))
    tipo_tecnico = models.CharField(max_length=20, choices=TIPO_TEC, verbose_name="Tipo de tecnico")
    tec_tac = models.BooleanField(verbose_name="Tec. TAC")
    # Defensa y otras Organizaciones
    ORG_DEF = (
        ('MTT', 'MTT'), ('FEI', 'FEI'), ('BPD-LR ', 'BPD-LR'), ('BPD-PTG ', 'BPD-PTG'), ('U/R', 'U/R'),
        ('Imp', 'Imprescindible'))

    orga_defensa = models.CharField(max_length=20, verbose_name="Organización defensa", choices=ORG_DEF)
    unidad_militar = models.CharField(max_length=20, verbose_name="Unidad Militar", blank=True)
    estado_mayor = models.CharField(max_length=20, verbose_name="Estado Mayor", blank=True)
    a_mision = models.CharField(verbose_name="Año de misión", blank=True, max_length=15)
    ORG_OPT = (('1', 'UJC'), ('2', 'PCC'))
    militancia = models.CharField(max_length=5, verbose_name="Militancia", choices=ORG_OPT, blank=True)
    org_masas = models.CharField(max_length=20, verbose_name="Organizaciones de masas")
    org_prof = models.CharField(max_length=20, verbose_name="Organizaciones profesionales", blank=True)
    org_cult = models.CharField(max_length=20, verbose_name="Organizaciones culturales", blank=True)

    # Talla
    zapato = models.CharField(max_length=4)
    saya = models.CharField(max_length=5, blank=True)
    blusa = models.CharField(max_length=4, blank=True)
    pullover = models.CharField(max_length=4)
    pitusa = models.CharField(max_length=5, blank=True)
    camisa = models.CharField(max_length=5, blank=True)
    derecho = models.BooleanField(verbose_name="Con derecho")

    def geturl(self):
        # return self.id
        return reverse('EditarTrabajador', kwargs={'trabajador_id': self.id})

    def __str__(self):
        return ' {} {} {}'.format(self.primer_nombre, self.segundo_nombre, self.apellidos)


class Movimiento(models.Model):
    fecha = models.DateField(max_length=20, verbose_name="Fecha del movimiento", blank=True, null=True)
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE)
    TIPO_OPT = (('1', 'Promoción'), ('2', 'Cambio de área'), ('3', 'Ambos'))
    tipo = models.CharField(max_length=100, verbose_name="Tipo de movimiento", blank=True, null=True,
                            default='No definido')
    cargo_ant = models.CharField(max_length=60, verbose_name="Cargo anterior", blank=True, null=True)
    cargo_act = models.CharField(max_length=60, verbose_name="Cargo actual", blank=True, null=True)
    area_ant = models.CharField(max_length=60, verbose_name="Departamento anterior", blank=True, null=True)
    area_act = models.CharField(max_length=60, verbose_name="Departamento actual", blank=True, null=True)
    cies_ant = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='CIES')
    cies_act = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='CIES')
    incre_res_ant = models.DecimalField(max_digits=5, decimal_places=2,
                                        verbose_name='Pago por perfeccionamiento anterior')
    incre_res_act = models.DecimalField(max_digits=5, decimal_places=2,
                                        verbose_name='Pago por perfeccionamiento actual')
    categoria_ant = models.CharField(max_length=15, verbose_name='Categoría ocupacional anterior')
    categoria_act = models.CharField(max_length=15, verbose_name='Categoría ocupacional actual')
    antiguedad_ant = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    antiguedad_act = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    salario_escala_ant = models.DecimalField(verbose_name='Salario escala anterior', max_digits=5, decimal_places=2,
                                             default=0.00)
    salario_escala_act = models.DecimalField(verbose_name='Salario escala actual', max_digits=5, decimal_places=2,
                                             default=0.00)
    escala_salarial_ant = models.CharField(max_length=5)
    escala_salarial_act = models.CharField(max_length=5)
    salario_total_ant = models.DecimalField(max_digits=7, verbose_name='Salario Total anterior', blank=True, null=True,
                                            decimal_places=2)
    salario_total_act = models.DecimalField(max_digits=7, verbose_name='Salario Total actual', blank=True, null=True,
                                            decimal_places=2)
    sal_plus_ant = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Salario plus anterior',
                                       default=0.00)
    sal_plus_act = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Salario plus actual', default=0.00)
    sal_cat_cient_ant = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Salario x cat. científica",
                                            blank=True, null=True, default=0.00)
    sal_cat_cient_act = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Salario x cat. científica",
                                            blank=True, null=True, default=0.00)

    def __str__(self):
        return 'Trabajador: {0} Movimiento: {1}'.format(self.trabajador, self.tipo)


class Cpl(models.Model):
    fecha = models.DateField()
    valor = models.DecimalField(max_digits=3, decimal_places=2)
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return 'Trabajador: {0} Valor CPL: {1} Fecha: {2}'.format(self.trabajador, self.valor, self.fecha)


class NucleoFamiliar(models.Model):
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE)
    PARENTESCO_OPT = (
        ('0', 'Padre'), ('1', 'Madre'), ('2', 'Hermano(a)'), ('3', 'Abuelo(a)'), ('4', 'Tio(a)'), ('5', 'Primo(a)'),
        ('6', 'Pareja'), ('7', 'Esposo(a)'), ('8', 'Hijastro(a)'), ('9', 'Madrasta'), ('10', 'Padrastro'),
        ('11', 'Otro'))
    parentesco = models.CharField(max_length=10, choices=PARENTESCO_OPT, blank=True, null=True)
    fecha_nac = models.DateField(verbose_name='Fecha de nacimiento', blank=True, null=True)
    enfermedades = models.CharField(max_length=100, verbose_name='Enfermedades que padece', default='Ninguna')
    vinc_lab = models.BooleanField(verbose_name='Vinculo laboral')
    salario_dev = models.DecimalField(max_digits=6, decimal_places=2, verbose_name='Salario que devenga', blank=True,
                                      null=True)

    def __str__(self):
        return self.trabajador.primer_nombre


class Baja(models.Model):
    primer_nombre = models.CharField(max_length=20, verbose_name='Primer nombre')
    segundo_nombre = models.CharField(max_length=20, blank=True, verbose_name='Segundo nombre')
    apellidos = models.CharField(max_length=60, verbose_name='Apellidos')
    ci = models.CharField(max_length=11, verbose_name='Carnet de Identidad', unique=True)
    causa = models.CharField(max_length=60, verbose_name='Causa de la baja', default='No definida')
    foto = models.ImageField(upload_to='fotos', verbose_name='Foto', blank=True)
    SEXO_OPT = (('M', 'Masculino'), ('F', 'Femenino'))
    sexo = models.CharField(max_length=1, choices=SEXO_OPT, verbose_name='Sexo', default=SEXO_OPT[0])
    ETNIA_OPT = (('B', 'Blanca'), ('M', 'Mestiza'), ('N', 'Negra'))
    etnia = models.CharField(max_length=10, choices=ETNIA_OPT, verbose_name='Etnia', default=ETNIA_OPT[0])
    lugar_nacimiento = models.CharField(max_length=30, verbose_name='Lugar de nacimiento', blank=True)
    telefono = models.CharField(max_length=8, verbose_name='Teléfono', blank=True)
    codigo_interno = models.CharField(max_length=3, unique=True, verbose_name='Código Interno')
    usuario = models.CharField(max_length=20, verbose_name='Usuario', blank=True, null=True)
    unidad_org = models.ForeignKey(UnidadOrg, on_delete=models.DO_NOTHING, verbose_name='Unidad organizacional')
    departamento = models.ForeignKey(Departamento, on_delete=models.DO_NOTHING, verbose_name='Departamento')
    cargo = models.ForeignKey(Cargo, on_delete=models.DO_NOTHING, verbose_name='Cargo')
    salario_escala = models.DecimalField(verbose_name='Salario escala', max_digits=5, decimal_places=2, default=0.00)
    motivo_baja = models.CharField(max_length=20, blank=True, verbose_name='Motivo de la Baja')
    cies = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='CIES')
    antiguedad = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    salario_total = models.DecimalField(max_digits=7, verbose_name='Salario Total', blank=True, null=True,
                                        decimal_places=2)
    incre_res = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Pago por perfeccionamiento')
    escala_salarial = models.ForeignKey(EscalaSalarial, on_delete=models.DO_NOTHING)
    categoria = models.CharField(max_length=15, verbose_name='Categoría ocupacional')
    fecha_alta = models.DateField(verbose_name="Fecha de alta al cargo")
    fecha_baja = models.DateField(verbose_name="Fecha de baja")
    fecha_disponible = models.DateField(blank=True, verbose_name="Fecha de inicio disponibilidad", null=True)
    fecha_ingreso = models.DateField(verbose_name="Fecha de ingreso al organismo")
    especialidad = models.ForeignKey(Especialidad, on_delete=models.DO_NOTHING, verbose_name="Especialidad", null=True,
                                     blank=True)
    anno_graduado = models.PositiveIntegerField(verbose_name="Año de graduado", null=True, blank=True)
    ESCOLARIDAD_OPT = (
        ('6to', '6to Grado'), ('9no', '9no Grado'), ('12mo', '12mo Grado'), ('TM', 'Técnico Medio'),
        ('OC', 'Obrero Calificado'),
        ('Univ', 'Universitario'))
    escolaridad = models.CharField(max_length=20, choices=ESCOLARIDAD_OPT, verbose_name="Escolaridad")
    sal_cat_cient = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Salario x cat. científica",
                                        blank=True, null=True, default=0.00)
    sal_plus = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Salario plus', default=0.00)
    salario_jornada_laboral = models.DecimalField(max_digits=5, verbose_name='Salario por Jornada Laboral', blank=True,
                                                  null=True, default=0.00, decimal_places=2)
    j_laboral = models.BooleanField(verbose_name='Jornada Laboral de 208 horas', default=False)

    def __str__(self):
        return '{} {} {} {}'.format(self.codigo_interno, self.primer_nombre, self.segundo_nombre, self.apellidos)


class Disponible(models.Model):
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE)
    fecha = models.DateField(verbose_name="Fecha de disponibilidad")

    def __str__(self):
        return self.trabajador.primer_nombre, self.trabajador.apellidos, self.trabajador.codigo_interno
