      PROGRAM add 
        IMPLICIT NONE
        INTEGER::i, L, N 
        REAL:: trash
        REAL(KIND=KIND(0.0D0)),DIMENSION(:),ALLOCATABLE:: Z, TZ, MAV, TMAV
        LOGICAL :: file_exists       

        READ (10,*) L
        READ (11,*) N
        ALLOCATE(Z(L))
        ALLOCATE(MAV(L))
        ALLOCATE(TMAV(L))
        ALLOCATE(TZ(L))
        Do i=1, L
          READ (12,*) Z(i), MAV(i)
        END DO

        INQUIRE(FILE="fort.13", EXIST=file_exists)

        IF (file_exists) THEN
          DO i=1, L
            READ (13,*) TZ(i), TMAV(i) 
          END DO
          CLOSE (13)
        ELSE
          TMAV = 0.0D0
          TZ = 0.0D0
        END IF
        DO i=1,L
          WRITE (13,*) TZ(i)+Z(i)/DBLE(N),TMAV(i)+MAV(i)/DBLE(N)
        END DO

      END PROGRAM add 

