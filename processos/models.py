# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ProcessosColetados(models.Model):
    consulta_data_etl = models.DateTimeField()
    consulta_resposta_status = models.CharField(max_length=400)
    processo_numero = models.CharField(max_length=20)
    processo_json = models.TextField()
    etl_tag_1 = models.TextField(blank=True, null=True)
    etl_checksumid_1 = models.TextField(unique=True)
    etl_dt_check = models.DateTimeField()
    etl_dt_criacao = models.DateTimeField()
    etl_dt_ult_atualiz = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'processos_coletados'

    def __str__(self):
        return self.processo_numero


class ProcessosDiasAColetar(models.Model):
    data_inicio = models.DateTimeField(blank=True, null=True)
    data_final = models.DateTimeField(blank=True, null=True)
    consulta_data_etl = models.DateTimeField(blank=True, null=True)
    consulta_resposta_status = models.CharField(max_length=400, blank=True, null=True)
    consulta_resposta_texto = models.CharField(max_length=400, blank=True, null=True)
    consulta_resposta_json = models.TextField(blank=True, null=True)  # This field type is a guess.
    consulta_resposta_raw = models.BinaryField(blank=True, null=True)
    etl_checksumid_1 = models.TextField(unique=True)
    etl_checksumid_2 = models.TextField()
    etl_dt_check = models.DateTimeField()
    etl_dt_criacao = models.DateTimeField()
    etl_dt_ult_atualiz = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'processos_dias_a_coletar'


class ReusProcessosColetados(models.Model):
    id_processos_coletados = models.IntegerField()
    consulta_data_etl = models.DateTimeField()
    processo_numero = models.CharField(max_length=20)
    etl_tag_1 = models.TextField(blank=True, null=True)
    pessoa_reu = models.CharField(max_length=400, blank=True, null=True)
    pessoa_tipo = models.CharField(max_length=8, blank=True, null=True)
    pessoa_doc_tipo = models.CharField(max_length=8, blank=True, null=True)
    pessoa_doc_codigo = models.CharField(max_length=36, blank=True, null=True)
    pessoa_doc_emissor = models.CharField(max_length=36, blank=True, null=True)
    etl_checksumid_1 = models.TextField(unique=True)
    etl_dt_check = models.DateTimeField()
    etl_dt_criacao = models.DateTimeField()
    etl_dt_ult_atualiz = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'reus_processos_coletados'

    def __str__(self):
        return self.pessoa_reu
