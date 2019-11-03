/*
Created by: Nadia Choudhury, Micha Beens
Status: Finished
Version: 2019.d8.v3
*/

/*Dropping the existing tables so we can recreate them*/
drop table if exists variants;
drop table if exists genes;
drop table if exists chromosomes;

/*The table that contains all infromation that is specific to a chromosome*/
create table chromosomes(
	chrom_id				int				auto_increment,
	chromosome				varchar(25)		not null        unique,
	primary key(chrom_id)
);

/*The table that contains all information that is specific to genes*/
create table genes(
	gene_id					int				auto_increment,
	chrom_id				int             not null,
	refseq_gene				varchar(255)    not null        unique,
	
	primary key(gene_id),
	foreign key(chrom_id)
	    references chromosomes(chrom_id)
	        on delete restrict
);

/*The table that contains all variant infromation that is relevant to our project*/
create table variants(
	variant_id				int				auto_increment,
	gene_id					int,
	begin				    int(20)			not null,
	reference				char(1)			not null,
	refseq_func				varchar(255),
	dbsnp138				varchar(255),
	1000g2015aug_eur		float,
	ljb2_sift				float,
	ljb2_polyphen2_hdiv		varchar(20),
	clinvar					varchar(255),
	
	primary key(variant_id),
	foreign key(gene_id)
	    references genes(gene_id)
	        on delete restrict
);
