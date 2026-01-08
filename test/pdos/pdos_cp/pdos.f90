      PROGRAM pdos
        IMPLICIT NONE
        INTEGER,PARAMETER :: nl=3834
        REAL,PARAMETER::fermi=-0.15307267246254
        INTEGER::i,j
        INTEGER::step
        REAL,PARAMETER::de=0.1
        REAL,DIMENSION(1:nl)::e, weight
        INTEGER,DIMENSION(:),ALLOCATABLE::dos
        REAL,DIMENSION(:),ALLOCATABLE::prdos

        OPEN (10,FILE='input.pdos')
        DO i=1,nl
           READ (10,*) e(i), weight(i)
        END DO
        CLOSE (10)

        step=(e(nl)-e(1))/de+1
        ALLOCATE(dos(1:step))
        ALLOCATE(prdos(1:step))
        dos=0
        prdos=0

        DO i=1,step
           DO j=1,nl
              IF (e(1)+(i-1)*de<=e(j) .AND. e(j)<e(1)+i*de) THEN
                 dos(i)=dos(i)+1
                 prdos(i)=prdos(i)+weight(j)
              END IF
           END DO
        END DO

!        PRINT *, step

        OPEN (11,FILE='output.pdos')
        DO i=1,step
           WRITE (11,*) e(1)+(i-1)*de+0.5*de-27.2114*fermi,prdos(i),dos(i)
        END DO
        CLOSE (11)
      END PROGRAM pdos

