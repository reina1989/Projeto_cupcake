create table if not exists produtos (
  id bigint generated always as identity primary key,
  nome text not null,
  descricao text,
  preco numeric(10,2) not null,
  imagem_url text
);
alter table produtos enable row level security;
drop policy if exists "ler produtos" on produtos;
create policy "ler produtos" on produtos for select using (true);

insert into produtos (nome, descricao, preco) values
 ('Cupcake de Baunilha', 'Massa fofinha com cobertura cremosa', 8.00),
 ('Cupcake de Chocolate', 'Chocolate intenso com ganache', 8.00),
 ('Cupcake de Morango', 'Recheio de morango de verdade', 8.00),
 ('Cupcake de Ninho', 'Creme de leite Ninho irresistível', 8.00);

create table if not exists pedidos (
  id bigint generated always as identity primary key,
  criado_em timestamptz default now(),
  cliente text, email text, telefone text,
  endereco text, pagamento text, itens text,
  total numeric(10,2)
);
alter table pedidos enable row level security;
drop policy if exists "criar pedidos" on pedidos;
create policy "criar pedidos" on pedidos for insert with check (true);
