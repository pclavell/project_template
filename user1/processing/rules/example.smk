rule example_rule1:
    resources:
        runtime = 60,
        threads = 112
    shell:
        """
        module load samtools
        samtools view {input.bam} > {output.sam}
        """

rule example_rule2:
    resources:
        runtime = 60,
        threads = 112
    shell:
        """
        module load samtools
        samtools sort {input.sam} > {output.sorted_sam}
        """