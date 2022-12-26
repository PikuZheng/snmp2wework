FROM alpine:3.16
COPY snmp2wework.py /app/
RUN apk add --no-cache py3-requests py3-snmp py3-twisted
EXPOSE 162/udp
CMD ["python3","-u","/app/snmp2wework.py"]
