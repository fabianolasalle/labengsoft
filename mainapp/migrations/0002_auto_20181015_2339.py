# Generated by Django 2.0.5 on 2018-10-16 02:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CartaoPostagem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nroCartao', models.CharField(max_length=10)),
                ('nroContrato', models.CharField(max_length=10)),
                ('codAdmin', models.CharField(max_length=8)),
                ('ativo', models.BooleanField(default=True)),
                ('vencimento', models.DateField()),
                ('codDR', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Destinatario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50)),
                ('cpfCnpj', models.CharField(max_length=14)),
                ('email', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Embalagem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descr', models.CharField(blank=True, max_length=50, null=True)),
                ('peso', models.FloatField(default=0.0)),
                ('ativo', models.NullBooleanField()),
                ('tipo', models.PositiveIntegerField(blank=True, default=1, null=True)),
                ('comprimento', models.FloatField(default=0.0)),
                ('largura', models.FloatField(default=0.0)),
                ('altura', models.FloatField(default=0.0)),
                ('diametro', models.FloatField(default=0.0)),
                ('obs', models.CharField(blank=True, max_length=300, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Endereco',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cep', models.CharField(max_length=10)),
                ('logradouro', models.CharField(max_length=100)),
                ('numero', models.CharField(max_length=5)),
                ('complemento', models.CharField(blank=True, max_length=10, null=True)),
                ('bairro', models.CharField(max_length=30)),
                ('cidade', models.CharField(max_length=30)),
                ('uf', models.CharField(max_length=2)),
                ('default', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='GrupoDestinatario',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=30)),
                ('descr', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ObjetoPostal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codRastreamento', models.CharField(max_length=100)),
                ('descr', models.CharField(max_length=50)),
                ('qtdObj', models.PositiveIntegerField(blank=True, null=True)),
                ('nf', models.CharField(blank=True, max_length=20, null=True)),
                ('nroPedido', models.CharField(blank=True, max_length=20, null=True)),
                ('obs', models.CharField(blank=True, max_length=300, null=True)),
                ('destinatario', models.ManyToManyField(to='mainapp.Destinatario')),
                ('embalagem', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='mainapp.Embalagem')),
                ('endSelecionado', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='mainapp.Endereco')),
            ],
        ),
        migrations.CreateModel(
            name='PreListaPostagem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fechada', models.BooleanField(default=False)),
                ('dataCriacao', models.DateField(auto_now=True)),
                ('qtdObjetos', models.PositiveIntegerField()),
                ('cartaoPostagem', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='mainapp.CartaoPostagem')),
                ('endSelecionado', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='mainapp.Endereco')),
                ('objetosPostais', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mainapp.ObjetoPostal')),
            ],
        ),
        migrations.CreateModel(
            name='Remetente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50)),
                ('cpfCnpj', models.CharField(max_length=14)),
                ('email', models.CharField(blank=True, max_length=50, null=True)),
                ('cartaoPostagem', models.ManyToManyField(to='mainapp.CartaoPostagem')),
                ('enderecos', models.ManyToManyField(to='mainapp.Endereco')),
            ],
        ),
        migrations.CreateModel(
            name='Servico',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('idServico', models.IntegerField()),
                ('codigo', models.IntegerField()),
                ('descr', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='SigepEnvironment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usuario', models.CharField(max_length=50)),
                ('senha', models.CharField(max_length=50)),
                ('cnpj', models.CharField(max_length=14)),
                ('nomeEmpresa', models.CharField(max_length=50)),
                ('ambiente', models.CharField(max_length=20)),
                ('ativo', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Telefone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero', models.CharField(max_length=15)),
                ('tipo', models.IntegerField(default=1)),
                ('default', models.BooleanField(default=False)),
            ],
        ),
        migrations.DeleteModel(
            name='Pessoa',
        ),
        migrations.AddField(
            model_name='remetente',
            name='telefones',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mainapp.Telefone'),
        ),
        migrations.AddField(
            model_name='prelistapostagem',
            name='remetente',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='mainapp.Remetente'),
        ),
        migrations.AddField(
            model_name='objetopostal',
            name='servico',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mainapp.Servico'),
        ),
        migrations.AddField(
            model_name='destinatario',
            name='enderecos',
            field=models.ManyToManyField(to='mainapp.Endereco'),
        ),
        migrations.AddField(
            model_name='destinatario',
            name='grupos',
            field=models.ManyToManyField(blank=True, null=True, to='mainapp.GrupoDestinatario'),
        ),
        migrations.AddField(
            model_name='destinatario',
            name='telefones',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='mainapp.Telefone'),
        ),
        migrations.AddField(
            model_name='cartaopostagem',
            name='servicos',
            field=models.ManyToManyField(to='mainapp.Servico'),
        ),
    ]
    