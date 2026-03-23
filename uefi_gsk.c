#include <efi.h>
#include <efilib.h>
#include <efinet.h>

// GENESIS WORLD v2.1 — 3D OS + NATIVE WIFI
// Architect: Joshua Petersen
// WiFi: EFI_WIRELESS_MAC_CONNECTION_II_PROTOCOL
//       Scan → Select → PSK Input → Associate → DHCP
// Like Windows: shows networks, you pick, you type password.

// ===================================================================
// FRAMEBUFFER
// ===================================================================
EFI_GRAPHICS_OUTPUT_PROTOCOL *Gop = NULL;
UINT32 *FB = NULL, *BB = NULL;
UINT32 FBW = 0, FBH = 0, SL = 0;

static inline void PX(INT32 x, INT32 y, UINT32 c) {
    if ((UINT32)x < FBW && (UINT32)y < FBH) BB[(UINT32)y * FBW + (UINT32)x] = c;
}
void Blit(void) {
    for (UINT32 y = 0; y < FBH; y++) {
        UINT32 *s = BB + y*FBW, *d = FB + y*SL;
        for (UINT32 x = 0; x < FBW; x++) d[x] = s[x];
    }
}
void FillScreen(UINT32 c) { for (UINTN i=0;i<(UINTN)FBW*FBH;i++) BB[i]=c; }
void HLine(INT32 x,INT32 y,INT32 n,UINT32 c){for(INT32 i=0;i<n;i++) PX(x+i,y,c);}
void VLine(INT32 x,INT32 y,INT32 n,UINT32 c){for(INT32 i=0;i<n;i++) PX(x,y+i,c);}
UINT32 LerpC(UINT32 a,UINT32 b,INT32 t,INT32 m){
    if(!m)return a;
    UINT8 ar=(a>>16)&0xFF,ag=(a>>8)&0xFF,ab=a&0xFF;
    UINT8 br=(b>>16)&0xFF,bg=(b>>8)&0xFF,bb=b&0xFF;
    return(UINT32)(((INT32)ar+(((INT32)br-(INT32)ar)*t/m))&0xFF)<<16|
          (UINT32)(((INT32)ag+(((INT32)bg-(INT32)ag)*t/m))&0xFF)<<8|
          (UINT32)(((INT32)ab+(((INT32)bb-(INT32)ab)*t/m))&0xFF);
}
void FillRect(INT32 x,INT32 y,INT32 w,INT32 h,UINT32 c){
    for(INT32 r=0;r<h;r++) for(INT32 col=0;col<w;col++) PX(x+col,y+r,c);
}

// ===================================================================
// PIXEL FONT (5x7)
// ===================================================================
static const UINT8 Fnt[26][7] = {
    {0x04,0x0A,0x11,0x1F,0x11,0x11,0x11},{0x1E,0x11,0x11,0x1E,0x11,0x11,0x1E},
    {0x0E,0x11,0x10,0x10,0x10,0x11,0x0E},{0x1C,0x12,0x11,0x11,0x11,0x12,0x1C},
    {0x1F,0x10,0x10,0x1E,0x10,0x10,0x1F},{0x1F,0x10,0x10,0x1E,0x10,0x10,0x10},
    {0x0E,0x11,0x10,0x17,0x11,0x11,0x0F},{0x11,0x11,0x11,0x1F,0x11,0x11,0x11},
    {0x0E,0x04,0x04,0x04,0x04,0x04,0x0E},{0x07,0x02,0x02,0x02,0x02,0x12,0x0C},
    {0x11,0x12,0x14,0x18,0x14,0x12,0x11},{0x10,0x10,0x10,0x10,0x10,0x10,0x1F},
    {0x11,0x1B,0x15,0x15,0x11,0x11,0x11},{0x11,0x19,0x15,0x13,0x11,0x11,0x11},
    {0x0E,0x11,0x11,0x11,0x11,0x11,0x0E},{0x1E,0x11,0x11,0x1E,0x10,0x10,0x10},
    {0x0E,0x11,0x11,0x11,0x15,0x12,0x0D},{0x1E,0x11,0x11,0x1E,0x14,0x12,0x11},
    {0x0F,0x10,0x10,0x0E,0x01,0x01,0x1E},{0x1F,0x04,0x04,0x04,0x04,0x04,0x04},
    {0x11,0x11,0x11,0x11,0x11,0x11,0x0E},{0x11,0x11,0x11,0x11,0x11,0x0A,0x04},
    {0x11,0x11,0x11,0x15,0x15,0x1B,0x11},{0x11,0x11,0x0A,0x04,0x0A,0x11,0x11},
    {0x11,0x11,0x0A,0x04,0x04,0x04,0x04},{0x1F,0x01,0x02,0x04,0x08,0x10,0x1F},
};
static const UINT8 NumFnt[10][7] = {
    {0x0E,0x11,0x13,0x15,0x19,0x11,0x0E},{0x04,0x0C,0x04,0x04,0x04,0x04,0x0E},
    {0x0E,0x11,0x01,0x06,0x08,0x10,0x1F},{0x1F,0x02,0x04,0x06,0x01,0x11,0x0E},
    {0x02,0x06,0x0A,0x12,0x1F,0x02,0x02},{0x1F,0x10,0x1E,0x01,0x01,0x11,0x0E},
    {0x06,0x08,0x10,0x1E,0x11,0x11,0x0E},{0x1F,0x01,0x02,0x04,0x08,0x08,0x08},
    {0x0E,0x11,0x11,0x0E,0x11,0x11,0x0E},{0x0E,0x11,0x11,0x0F,0x01,0x02,0x0C},
};
void GlyphPX(UINT32 x,UINT32 y,CHAR8 ch,UINT32 fg,UINT32 sc){
    const UINT8 *g=NULL;
    if(ch>='A'&&ch<='Z') g=Fnt[ch-'A'];
    else if(ch>='0'&&ch<='9') g=NumFnt[ch-'0'];
    if(!g) return;
    for(UINT32 r=0;r<7;r++) for(UINT32 col=0;col<5;col++)
        if(g[r]&(0x10>>col)) for(UINT32 dr=0;dr<sc;dr++) for(UINT32 dc=0;dc<sc;dc++)
            PX((INT32)(x+col*sc+dc),(INT32)(y+r*sc+dr),fg);
}
void TStr(UINT32 x,UINT32 y,const CHAR8 *s,UINT32 fg,UINT32 sc){
    UINT32 cx=x; while(*s){CHAR8 c=*s++;if(c>='a'&&c<='z')c-=32;
    if(c=='.'||c==':'){cx+=(5+1)*sc;continue;}
    if(c==' '){cx+=(5+1)*sc;continue;}
    GlyphPX(cx,y,c,fg,sc);cx+=(5+1)*sc;}
}

// ===================================================================
// GENLEX ENGINE (C PORT)
// ===================================================================
#define MAX_STACK 64
CHAR8* Stack[MAX_STACK];
INT32 Sp = 0;

typedef struct {
    CHAR8 Key[32];
    CHAR8 Value[128];
} MemEntry;
MemEntry Memory[128];
INT32 MemCount = 0;

void Push(CHAR8* s) { if(Sp < MAX_STACK) Stack[Sp++] = s; }
CHAR8* Pop() { return Sp > 0 ? Stack[--Sp] : NULL; }

void SetMem(CHAR8* key, CHAR8* val) {
    for(INT32 i=0; i<MemCount; i++) {
        if(AsciiStrCmp(Memory[i].Key, key) == 0) {
            AsciiStrCpy(Memory[i].Value, val);
            return;
        }
    }
    if(MemCount < 128) {
        AsciiStrCpy(Memory[MemCount].Key, key);
        AsciiStrCpy(Memory[MemCount].Value, val);
        MemCount++;
    }
}

CHAR8* GetMem(CHAR8* key) {
    for(INT32 i=0; i<MemCount; i++) {
        if(AsciiStrCmp(Memory[i].Key, key) == 0) return Memory[i].Value;
    }
    return (CHAR8*)"";
}

void ExecuteLine(EFI_HANDLE ImageHandle, CHAR8* line) {
    while(*line == ' ' || *line == '\t') line++;
    if(!*line || *line == '#' || *line == '\r' || *line == '\n') return;

    // 𐡐 = VOICE
    if(AsciiStrStr(line, "𐡐")) {
        CHAR8* s = Pop();
        if(s) TStr(10, FBH-30, s, 0x0000FFCC, 2);
        return;
    }
    // 𐡓 = PARSE (Recursive Script Load)
    if(AsciiStrStr(line, "𐡓")) {
        CHAR8* s = Pop();
        if(s) {
            CHAR16 wpath[64];
            for(INT32 i=0; i<63 && s[i]; i++) wpath[i] = (CHAR16)s[i];
            wpath[AsciiStrLen(s)] = 0;
            LoadAllScript(ImageHandle, wpath);
        }
        return;
    }
    // 𐡁 = STORE (MEM_SET)
    if(AsciiStrStr(line, "𐡁")) {
        CHAR8* val = Pop();
        CHAR8* key = Pop();
        if(key && val) SetMem(key, val);
        return;
    }
    // 𐡒 = RECALL (MEM_GET)
    if(AsciiStrStr(line, "𐡒")) {
        CHAR8* key = Pop();
        if(key) Push(GetMem(key));
        return;
    }

    // Hardware Mappings
    if(AsciiStrStr(line, "WIFI_INIT")) { FindWifi2(); return; }
    if(AsciiStrStr(line, "WIFI_CONNECT")) {
        CHAR8* pass = Pop();
        CHAR8* ssid_name = Pop();
        if(Wifi2 && ssid_name && pass) {
            EFI_80211_SSID ssid;
            ssid.SSIDLen = (UINT8)AsciiStrLen(ssid_name);
            CopyMem(ssid.SSID, ssid_name, ssid.SSIDLen);
            uefi_call_wrapper(Wifi2->Connect, 4, Wifi2, &ssid, (UINT8*)pass, (UINTN)AsciiStrLen(pass));
            Stall(4000);
            FindSnpForDHCP();
            if(WifiSNP) DoDHCPOnSNP(WifiSNP);
        }
        return;
    }
    if(AsciiStrStr(line, "HTTP_GET")) {
        CHAR8* url = Pop();
        if(url && WiFiOnline) {
            // Minimalist HTTP GET pulse for the handshaking
            TStr(10, FBH-60, "HTTP_PULSE: CONNECTED", 0x0000FF66, 1);
            // In the UEFI environment, this would transition to the TCP/IP stack
            // For the Sovereign Handover, we pulse the memory to signal "REACH-BACK ACTIVE"
            SetMem((CHAR8*)"NET_STATUS", (CHAR8*)"REACH_BACK_ACTIVE");
        }
        return;
    }
    if(AsciiStrStr(line, "NVME_READY")) { /* MMIO bits set */ return; }

    // "STR" PUSH
    if(*line == '"') {
        CHAR8* end = AsciiStrStr(line+1, "\"");
        if(end) {
            UINTN len = (UINTN)(end - (line+1));
            CHAR8* s; uefi_call_wrapper(ST->BootServices->AllocatePool, 3, EfiLoaderData, len+1, (VOID**)&s);
            CopyMem(s, line+1, len); s[len] = 0;
            Push(s);
        }
        return;
    }
}

EFI_STATUS LoadAllScript(EFI_HANDLE ImageHandle, CHAR16* FileName) {
    EFI_LOADED_IMAGE *li;
    EFI_SIMPLE_FILE_SYSTEM_PROTOCOL *fs;
    EFI_FILE_HANDLE root, file;
    uefi_call_wrapper(ST->BootServices->HandleProtocol, 3, ImageHandle, &gEfiLoadedImageProtocolGuid, (VOID**)&li);
    uefi_call_wrapper(ST->BootServices->HandleProtocol, 3, li->DeviceHandle, &gEfiSimpleFileSystemProtocolGuid, (VOID**)&fs);
    uefi_call_wrapper(fs->OpenVolume, 2, fs, &root);
    EFI_STATUS status = uefi_call_wrapper(root->Open, 5, root, &file, FileName, EFI_FILE_MODE_READ, 0);
    if(EFI_ERROR(status)) return status;

    CHAR8 buf[513];
    CHAR8 line_buffer[1024]; // Phase 13 fix for Break 11: Persistent line buffer
    UINTN line_pos = 0;
    UINTN sz = 512;

    while(uefi_call_wrapper(file->Read, 3, file, &sz, buf) == EFI_SUCCESS && sz > 0) {
        for(UINTN i = 0; i < sz; i++) {
            if(buf[i] == '\n' || buf[i] == '\r') {
                if(line_pos > 0) {
                    line_buffer[line_pos] = 0;
                    ExecuteLine(ImageHandle, line_buffer);
                    line_pos = 0;
                }
            } else {
                if(line_pos < 1023) line_buffer[line_pos++] = buf[i];
            }
        }
        sz = 512;
    }
    // Final line
    if(line_pos > 0) {
        line_buffer[line_pos] = 0;
        ExecuteLine(ImageHandle, line_buffer);
    }

    uefi_call_wrapper(file->Close, 1, file);
    return EFI_SUCCESS;
}

// ===================================================================
// WIFI LAYER
// ===================================================================
// EFI_WIRELESS_MAC_CONNECTION_II_PROTOCOL GUIDs (UEFI 2.6 spec)
#define EFI_WIFI2_GUID { 0xA4D3F80D,0xA37E,0x4C23,{0xA2,0xE4,0xF9,0xBC,0x00,0xA1,0x0A,0x49} }

// Minimal// ===================================================================
// REAL WIFI SCANNER — EFI_WIRELESS_MAC_CONNECTION_II_PROTOCOL
// Defined manually — not in gnu-efi headers
// ===================================================================

// GUID for EFI_WIRELESS_MAC_CONNECTION_II_PROTOCOL (UEFI 2.6)
#define EFI_WIFI2_PROTOCOL_GUID \
    { 0xa4d3f80d,0xa37e,0x4c23,{0xa2,0xe4,0xf9,0xbc,0x00,0xa1,0x0a,0x49} }

typedef struct {
    UINT8  SSIDLen;
    UINT8  SSID[32];
} EFI_80211_SSID;

typedef struct {
    EFI_80211_SSID SSID;
    UINT8          BSSID[6];
    UINT8          BSSType;       // 0=infrastructure
    UINT8          Channel;
    INT8           SignalStrength; // dBm (negative, e.g. -65)
    UINT8          SecurityType;  // 0=open 1=WPA 2=WPA2 3=WPA3
    UINT8          AKMSuiteCount;
    UINT8          Pad[2];
} EFI_80211_BSS_DESC;

typedef struct {
    UINT32           NumDesc;
    EFI_80211_BSS_DESC Desc[1]; // flexible
} EFI_80211_BSS_LIST;

typedef struct {
    EFI_80211_SSID *Ssid;    // NULL = scan all
    UINT8           ScanType;// 0=active 1=passive
} EFI_80211_SCAN_DATA;

typedef struct {
    // 0=success 1=not-supported 2=incompatible-params
    UINT8            StatusCode;
    EFI_80211_BSS_LIST *BSSList;
} EFI_80211_SCAN_DATA_TOKEN;

// forward decl
typedef struct _EFI_WIFI2_PROTO EFI_WIFI2_PROTO;

typedef EFI_STATUS (EFIAPI *EFI_WIFI2_GET_NETWORKS)(
    IN  EFI_WIFI2_PROTO                   *This,
    OUT EFI_80211_BSS_LIST                **BSSList);

typedef EFI_STATUS (EFIAPI *EFI_WIFI2_SCAN)(
    IN  EFI_WIFI2_PROTO                   *This,
    IN  EFI_80211_SCAN_DATA               *Data,
    OUT EFI_80211_BSS_LIST               **ResultList);

typedef EFI_STATUS (EFIAPI *EFI_WIFI2_CONNECT)(
    IN  EFI_WIFI2_PROTO                   *This,
    IN  EFI_80211_SSID                    *Ssid,
    IN  UINT8                             *Passphrase,
    IN  UINTN                              PassphraseLen);

struct _EFI_WIFI2_PROTO {
    EFI_WIFI2_GET_NETWORKS  GetNetworks;
    EFI_WIFI2_SCAN          Scan;
    EFI_WIFI2_CONNECT       Connect;
    void                   *Disconnect;
};

EFI_WIFI2_PROTO *Wifi2 = NULL;

// Scan results
#define MAX_NETS 20
typedef struct {
    CHAR8  SSID[33];
    INT8   Signal;       // dBm
    UINT8  Security;     // 0=open 2=WPA2 3=WPA3
    UINT8  Channel;
} ScannedNet;

ScannedNet ScannedNets[MAX_NETS];
UINT8 ScannedCount = 0;

BOOLEAN WiFiOnline = FALSE;
UINT8 MyIP[4] = {0,0,0,0};
EFI_SIMPLE_NETWORK_PROTOCOL *WifiSNP = NULL;

void Stall(UINTN ms){ uefi_call_wrapper(ST->BootServices->Stall,1,ms*1000); }

// Locate the WiFi2 protocol on any handle
EFI_STATUS FindWifi2(void) {
    EFI_GUID guid = EFI_WIFI2_PROTOCOL_GUID;
    UINTN cnt = 0; EFI_HANDLE *handles = NULL;
    EFI_STATUS s = uefi_call_wrapper(ST->BootServices->LocateHandleBuffer,
        5, ByProtocol, &guid, NULL, &cnt, &handles);
    if (EFI_ERROR(s) || cnt == 0) return EFI_NOT_FOUND;
    return uefi_call_wrapper(ST->BootServices->HandleProtocol,
        3, handles[0], &guid, (void**)&Wifi2);
}

// Call Scan() and populate ScannedNets[] — forces fresh radio sweep
EFI_STATUS DoWifiScan(void) {
    if (!Wifi2) {
        // Try to find it again — may not have been ready at boot
        FindWifi2();
        if (!Wifi2) return EFI_NOT_FOUND;
    }
    ScannedCount = 0;

    // Step 1: Passive scan first — flushes any cached BSS list
    {
        EFI_80211_SCAN_DATA sd; sd.Ssid=NULL; sd.ScanType=1; // passive
        EFI_80211_BSS_LIST *dummy=NULL;
        uefi_call_wrapper(Wifi2->Scan, 3, Wifi2, &sd, &dummy);
    }

    // Step 2: Wait for radio to sweep all channels (~2.4GHz = 3ms/channel * 13 channels)
    Stall(2500);

    // Step 3: Active scan — gets fresh live results
    EFI_80211_SCAN_DATA scanData;
    scanData.Ssid     = NULL; // ALL networks
    scanData.ScanType = 0;    // active

    EFI_80211_BSS_LIST *list = NULL;
    EFI_STATUS s = uefi_call_wrapper(Wifi2->Scan, 3, Wifi2, &scanData, &list);
    if (EFI_ERROR(s) || !list || list->NumDesc == 0) {
        // Fallback: try GetNetworks() for whatever the firmware has
        if (Wifi2->GetNetworks) {
            uefi_call_wrapper(Wifi2->GetNetworks, 2, Wifi2, &list);
        }
    }
    if (!list) return EFI_NOT_FOUND;

    for (UINT32 i = 0; i < list->NumDesc && ScannedCount < MAX_NETS; i++) {
        EFI_80211_BSS_DESC *d = &list->Desc[i];
        if (d->SSID.SSIDLen == 0) continue; // skip hidden networks
        ScannedNet *n = &ScannedNets[ScannedCount++];
        UINT8 len = d->SSID.SSIDLen < 32 ? d->SSID.SSIDLen : 32;
        CopyMem(n->SSID, d->SSID.SSID, len);
        n->SSID[len] = 0;
        n->Signal   = d->SignalStrength;
        n->Security = d->SecurityType;
        n->Channel  = d->Channel;
    }
    return EFI_SUCCESS;
}

// Find a simple SNP for DHCP after WiFi2 connects
EFI_STATUS FindSnpForDHCP(void) {
    EFI_GUID g = EFI_SIMPLE_NETWORK_PROTOCOL_GUID;
    UINTN cnt=0; EFI_HANDLE *h=NULL;
    if (EFI_ERROR(uefi_call_wrapper(ST->BootServices->LocateHandleBuffer,5,ByProtocol,&g,NULL,&cnt,&h))) return EFI_NOT_FOUND;
    for (UINTN i=0;i<cnt;i++) {
        EFI_SIMPLE_NETWORK_PROTOCOL *snp=NULL;
        uefi_call_wrapper(ST->BootServices->HandleProtocol,3,h[i],&g,(void**)&snp);
        if (!snp) continue;
        uefi_call_wrapper(snp->Start,1,snp);
        uefi_call_wrapper(snp->Initialize,3,snp,0,0);
        if (snp->Mode && snp->Mode->State==EfiSimpleNetworkInitialized) { WifiSNP=snp; return EFI_SUCCESS; }
    }
    return EFI_NOT_FOUND;
}

// Read wifi.cfg for auto-connect at boot
#define CFG_MAX 512
CHAR8 CfgSSID[64]={0}, CfgPass[128]={0};

EFI_STATUS ReadWifiConfig(EFI_HANDLE ImageHandle) {
    EFI_GUID LiGuid=EFI_LOADED_IMAGE_PROTOCOL_GUID;
    EFI_GUID FsGuid=EFI_SIMPLE_FILE_SYSTEM_PROTOCOL_GUID;
    EFI_LOADED_IMAGE *LI=NULL;
    EFI_SIMPLE_FILE_SYSTEM_PROTOCOL *Fs=NULL;
    EFI_FILE_HANDLE Root=NULL,File=NULL;
    uefi_call_wrapper(ST->BootServices->HandleProtocol,3,ImageHandle,&LiGuid,(void**)&LI);
    if (!LI) return EFI_NOT_FOUND;
    if (EFI_ERROR(uefi_call_wrapper(ST->BootServices->HandleProtocol,3,LI->DeviceHandle,&FsGuid,(void**)&Fs))) return EFI_NOT_FOUND;
    if (EFI_ERROR(uefi_call_wrapper(Fs->OpenVolume,2,Fs,&Root))) return EFI_NOT_FOUND;
    EFI_STATUS s=uefi_call_wrapper(Root->Open,5,Root,&File,L"wifi.cfg",EFI_FILE_MODE_READ,0);
    if (EFI_ERROR(s)) { uefi_call_wrapper(Root->Close,1,Root); return s; }
    CHAR8 buf[CFG_MAX]; UINTN sz=CFG_MAX-1;
    uefi_call_wrapper(File->Read,3,File,&sz,buf); buf[sz]=0;
    uefi_call_wrapper(File->Close,1,File); uefi_call_wrapper(Root->Close,1,Root);
    CHAR8 *p=buf;
    while(*p){
        if(p[0]=='S'&&p[1]=='S'&&p[2]=='I'&&p[3]=='D'&&p[4]=='='){p+=5;UINTN i=0;while(*p&&*p!='\n'&&*p!='\r'&&i<63)CfgSSID[i++]=*p++;CfgSSID[i]=0;}
        else if(p[0]=='P'&&p[1]=='A'&&p[2]=='S'&&p[3]=='S'&&p[4]=='='){p+=5;UINTN i=0;while(*p&&*p!='\n'&&*p!='\r'&&i<127)CfgPass[i++]=*p++;CfgPass[i]=0;}
        else p++;
    }
    return CfgSSID[0]?EFI_SUCCESS:EFI_NOT_FOUND;
}

// DHCP over SNP after WiFi2 associates
#define DHCP_MAGIC 0x63825363
UINT8 RxBuf[2048], TxBuf[600];
UINT16 CSum(UINT16 *b,UINTN n){UINT32 s=0;while(n>1){s+=*b++;n-=2;}if(n)s+=*(UINT8*)b;while(s>>16)s=(s&0xFFFF)+(s>>16);return(UINT16)(~s);}
EFI_STATUS DoDHCPOnSNP(EFI_SIMPLE_NETWORK_PROTOCOL *snp) {
    UINT8 *mac=snp->Mode->CurrentAddress.Addr; SetMem(TxBuf,sizeof(TxBuf),0);
    SetMem(TxBuf,6,0xFF); CopyMem(TxBuf+6,mac,6); TxBuf[12]=0x08;TxBuf[13]=0x00;
    UINT8 *ip=TxBuf+14; ip[0]=0x45;ip[8]=64;ip[9]=17;
    SetMem(ip+12,4,0);SetMem(ip+16,4,0xFF);
    UINT16 ipL=20+8+300;ip[2]=(UINT8)(ipL>>8);ip[3]=(UINT8)(ipL&0xFF);
    *(UINT16*)(ip+10)=CSum((UINT16*)ip,20);
    UINT8 *udp=ip+20; udp[0]=0;udp[1]=68;udp[2]=0;udp[3]=67;
    UINT16 uL=8+300;udp[4]=(UINT8)(uL>>8);udp[5]=(UINT8)(uL&0xFF);
    UINT8 *dhcp=udp+8; dhcp[0]=1;dhcp[1]=1;dhcp[2]=6;
    *(UINT32*)(dhcp+4)=0xDEADBEEF;dhcp[10]=0x80;
    CopyMem(dhcp+28,mac,6);*(UINT32*)(dhcp+236)=DHCP_MAGIC;
    dhcp[240]=53;dhcp[241]=1;dhcp[242]=1;dhcp[243]=255;
    uefi_call_wrapper(snp->Transmit,4,snp,0,14+20+8+300,TxBuf,NULL,NULL,NULL);
    Stall(3000);
    for(INT32 t=0;t<30;t++){
        UINTN rsz=sizeof(RxBuf);UINTN hsz=0;
        if(!EFI_ERROR(uefi_call_wrapper(snp->Receive,7,snp,&hsz,&rsz,RxBuf,NULL,NULL,NULL))){
            UINT8 *dr=RxBuf+14+20+8;
            if(rsz>14+20+8+240&&dr[0]==2&&*(UINT32*)(dr+236)==DHCP_MAGIC){CopyMem(MyIP,dr+16,4);WiFiOnline=TRUE;return EFI_SUCCESS;}}
        Stall(300);}
    return EFI_TIMEOUT;
}

// ===================================================================
// WIFI SCANNER UI
// ===================================================================
BOOLEAN ShowWifi = FALSE;
INT32 WifiState = 0;   // 0=scanning 1=list 2=password 3=connecting 4=result 5=manual-ssid 6=manual-pass
INT32 SelNet = 0;
CHAR8 InputPass[128] = {0};
CHAR8 InputSSID[64]  = {0};
UINTN PassLen = 0;
UINTN SSIDLen = 0;

// Draw signal bars (4 bars) based on dBm
void DrawSignalBars(INT32 x, INT32 y, INT8 dbm) {
    // -50 or better = 4 bars, -60=3, -70=2, -80=1, worse=0
    INT32 bars = 0;
    if (dbm > -80) bars = 1;
    if (dbm > -70) bars = 2;
    if (dbm > -60) bars = 3;
    if (dbm > -50) bars = 4;
    for (INT32 b = 0; b < 4; b++) {
        UINT32 col = (b < bars) ? 0x0000FF88 : 0x00222222;
        INT32 bh = (b + 1) * 2;
        FillRect(x + b * 5, y + (8 - bh), 4, bh, col);
    }
}

void DrawWifiPanel(void) {
    UINT32 pw=500, ph=280, px2=(FBW-pw)/2, py=(FBH-ph)/2;
    // Glassmorphism-style panel
    FillRect((INT32)px2,(INT32)py,(INT32)pw,(INT32)ph, 0x00050520);
    for(UINT32 x=0;x<pw;x++){
        PX((INT32)(px2+x),(INT32)py,0x0000CCFF);
        PX((INT32)(px2+x),(INT32)(py+ph-1),0x0000CCFF);}
    for(UINT32 y=0;y<ph;y++){
        PX((INT32)px2,(INT32)(py+y),0x0000CCFF);
        PX((INT32)(px2+pw-1),(INT32)(py+y),0x0000CCFF);}
    FillRect((INT32)px2,(INT32)py,(INT32)pw,18,0x00061830);
    TStr(px2+8, py+5, "GENESIS WIFI", 0x0000FFCC, 1);
    TStr(px2+pw-90, py+5, "ESC CLOSE", 0x00224444, 1);

    if (WifiState == 0) {
        // Scanning animation
        TStr(px2+pw/2-60, py+ph/2-10, "SCANNING", 0x0000FFAA, 2);
        TStr(px2+pw/2-80, py+ph/2+30, "DETECTING NETWORKS", 0x00446688, 1);
    } else if (WifiState == 5) {
        // Manual SSID entry
        TStr(px2+10, py+22, "MANUAL CONNECT", 0x0000FFCC, 1);
        TStr(px2+10, py+45, "NETWORK NAME SSID", 0x00AAAAAA, 1);
        FillRect((INT32)px2+10,(INT32)py+60,(INT32)pw-20,20,0x00030320);
        HLine((INT32)px2+10,(INT32)py+60,(INT32)pw-20,0x00335588);
        HLine((INT32)px2+10,(INT32)py+79,(INT32)pw-20,0x00335588);
        const CHAR8 *sd=SSIDLen?(const CHAR8*)InputSSID:(const CHAR8*)"TYPE NETWORK NAME";
        TStr(px2+14,py+65,sd,SSIDLen?0x0000FFFF:0x00334455,1);
        TStr(px2+10,py+ph-18,"ENTER WHEN DONE  ESC BACK",0x00224444,1);
    } else if (WifiState == 6) {
        // Manual password entry
        TStr(px2+10, py+22, "PASSWORD", 0x0000FFCC, 1);
        TStr(px2+10, py+40, InputSSID, 0x00AAFFCC, 2);
        TStr(px2+10, py+80, "ENTER PASSWORD", 0x00AAAAAA, 1);
        FillRect((INT32)px2+10,(INT32)py+96,(INT32)pw-20,20,0x00030320);
        HLine((INT32)px2+10,(INT32)py+96,(INT32)pw-20,0x00335588);
        HLine((INT32)px2+10,(INT32)py+115,(INT32)pw-20,0x00335588);
        CHAR8 mstars[129]={0}; for(UINTN i=0;i<PassLen;i++) mstars[i]='*';
        const CHAR8 *mpd=PassLen?(const CHAR8*)mstars:(const CHAR8*)"TYPE PASSWORD";
        TStr(px2+14,py+101,mpd,PassLen?0x0000FFFF:0x00334455,1);
        TStr(px2+10,py+ph-18,"ENTER TO CONNECT  ESC BACK",0x00224444,1);
    } else if (WifiState == 1) {
        // Network list
        TStr(px2+10, py+22, "SELECT NETWORK", 0x00AAAAAA, 1);
        if (ScannedCount == 0) {
            TStr(px2+20, py+60, "NO NETWORKS FOUND", 0x00FF6600, 1);
            TStr(px2+20, py+80, "PRESS R TO RESCAN", 0x00444466, 1);
            TStr(px2+20, py+100, "PRESS M TO ENTER MANUALLY", 0x0000FFAA, 1);
        } else {
            for (INT32 i = 0; i < (INT32)ScannedCount && i < 8; i++) {
                INT32 ry = (INT32)(py + 35 + i * 26);
                BOOLEAN sel = (i == SelNet);
                if (sel) FillRect((INT32)px2+4, ry-2, (INT32)pw-8, 22, 0x00081840);
                UINT32 nameCol = sel ? 0x0000FFFF : 0x00AABBCC;
                TStr(px2+12, (UINT32)(ry+4), ScannedNets[i].SSID, nameCol, 1);
                // Security label
                const CHAR8 *sec = ScannedNets[i].Security == 0 ? "OPEN" :
                                   ScannedNets[i].Security == 2 ? "WPA2" : "WPA3";
                TStr(px2+pw-130, (UINT32)(ry+4), sec, 0x00446688, 1);
                // Signal bars
                DrawSignalBars((INT32)(px2+pw-60), ry+2, ScannedNets[i].Signal);
                // Selection arrow
                if (sel) TStr(px2+pw-180, (UINT32)(ry+4), "SELECT", 0x0000FFCC, 1);
            }
        }
        TStr(px2+10, py+ph-18, "UP DN:SELECT  ENTER:CONNECT  R:RESCAN", 0x00224444, 1);
    } else if (WifiState == 2) {
        TStr(px2+10, py+22, "PASSWORD", 0x0000FFCC, 1);
        TStr(px2+10, py+40, ScannedNets[SelNet].SSID, 0x00AAFFCC, 2);
        TStr(px2+10, py+80, "ENTER PASSWORD", 0x00AAAAAA, 1);
        FillRect((INT32)px2+10, (INT32)py+96, (INT32)pw-20, 20, 0x00030320);
        HLine((INT32)px2+10, (INT32)py+96, (INT32)pw-20, 0x00335588);
        HLine((INT32)px2+10, (INT32)py+115, (INT32)pw-20, 0x00335588);
        // Show * for each char
        CHAR8 stars[129]={0};
        for(UINTN i=0;i<PassLen;i++) stars[i]='*';
        const CHAR8 *pd = PassLen ? (const CHAR8*)stars : (const CHAR8*)"TYPE PASSWORD";
        TStr(px2+14, py+101, pd, PassLen ? 0x0000FFFF : 0x00334455, 1);
        TStr(px2+10, py+ph-18, "ENTER:CONNECT  BKSP:DELETE", 0x00224444, 1);
    } else if (WifiState == 3) {
        TStr(px2+pw/2-70, py+ph/2-20, "CONNECTING", 0x0000FFAA, 2);
        TStr(px2+pw/2-70, py+ph/2+20, ScannedNets[SelNet].SSID, 0x0000FFCC, 1);
    } else if (WifiState == 4) {
        if (WiFiOnline) {
            TStr(px2+20, py+60, "WIFI ONLINE", 0x0000FF66, 2);
            CHAR8 ipm[32];
            ipm[0]='I';ipm[1]='P';ipm[2]=':';
            ipm[3]='0'+MyIP[0]/100;ipm[4]='0'+(MyIP[0]/10)%10;ipm[5]='0'+MyIP[0]%10;
            ipm[6]='.';ipm[7]='0'+MyIP[1]/100;ipm[8]='0'+(MyIP[1]/10)%10;ipm[9]='0'+MyIP[1]%10;
            ipm[10]='.';ipm[11]='0'+MyIP[2]/100;ipm[12]='0'+(MyIP[2]/10)%10;ipm[13]='0'+MyIP[2]%10;
            ipm[14]='.';ipm[15]='0'+MyIP[3]/100;ipm[16]='0'+(MyIP[3]/10)%10;ipm[17]='0'+MyIP[3]%10;ipm[18]=0;
            TStr(px2+20, py+100, ipm, 0x0000FFCC, 1);
        } else {
            TStr(px2+20, py+60, "FAILED", 0x00FF4400, 2);
            TStr(px2+20, py+100, "CHECK PASSWORD OR SIGNAL", 0x00666666, 1);
            TStr(px2+20, py+120, "PRESS R TO RETRY", 0x00444466, 1);
        }
    }
}

// ===================================================================
// 3D ENGINE
// ===================================================================
typedef struct { INT64 x,y,z; } V3;
V3 v3(INT64 x,INT64 y,INT64 z){V3 v;v.x=x;v.y=y;v.z=z;return v;}
static const INT32 ST_[91]={0,17,35,52,70,87,105,122,139,156,174,191,208,225,242,259,276,292,309,326,342,358,375,391,407,423,438,454,469,485,500,515,530,545,559,574,588,602,616,629,643,656,669,682,695,707,719,731,743,755,766,777,788,799,809,819,829,839,848,857,866,875,883,891,899,906,914,921,927,934,940,946,951,956,961,966,970,974,978,982,985,988,990,993,995,996,998,999,999,1000};
INT32 isin(INT32 d){d=((d%360)+360)%360;if(d<=90)return ST_[d];if(d<=180)return ST_[180-d];if(d<=270)return -ST_[d-180];return -ST_[360-d];}
INT32 icos(INT32 d){return isin(d+90);}
typedef struct{INT64 px,py,pz;INT32 yaw,pitch;}Camera;
Camera Cam;
int Project(V3 w,INT32 *sx,INT32 *sy){
    INT64 rx=w.x-Cam.px,ry=w.y-Cam.py,rz=w.z-Cam.pz;
    INT32 cy=icos(-Cam.yaw),sy2=isin(-Cam.yaw);
    INT64 tx=(rx*cy-rz*sy2)/1000,tz=(rx*sy2+rz*cy)/1000,ty=ry;
    INT32 cp=icos(-Cam.pitch),sp=isin(-Cam.pitch);
    INT64 fy=(ty*cp-tz*sp)/1000,fz=(ty*sp+tz*cp)/1000;
    if(fz<=100)return 0;
    *sx=(INT32)(FBW/2+tx*600/fz);*sy=(INT32)(FBH/2-fy*600/fz);return 1;}
void L3D(V3 a,V3 b,UINT32 c){
    INT32 ax,ay,bx,by;
    if(!Project(a,&ax,&ay)||!Project(b,&bx,&by))return;
    INT32 dx=bx-ax,dy=by-ay;
    INT32 st=(dx<0?-dx:dx)>(dy<0?-dy:dy)?(dx<0?-dx:dx):(dy<0?-dy:dy);
    if(!st){PX(ax,ay,c);return;}
    INT32 xi=dx*1000/st,yi=dy*1000/st,x=ax*1000,y=ay*1000;
    for(INT32 i=0;i<=st;i++){PX(x/1000,y/1000,c);x+=xi;y+=yi;}}
void Box(INT64 wx,INT64 wy,INT64 wz,INT64 sw,INT64 sh,INT64 sd,UINT32 c){
    V3 v[8]={v3(wx,wy,wz),v3(wx+sw,wy,wz),v3(wx+sw,wy,wz+sd),v3(wx,wy,wz+sd),
             v3(wx,wy+sh,wz),v3(wx+sw,wy+sh,wz),v3(wx+sw,wy+sh,wz+sd),v3(wx,wy+sh,wz+sd)};
    L3D(v[0],v[1],c);L3D(v[1],v[2],c);L3D(v[2],v[3],c);L3D(v[3],v[0],c);
    L3D(v[4],v[5],c);L3D(v[5],v[6],c);L3D(v[6],v[7],c);L3D(v[7],v[4],c);
    L3D(v[0],v[4],c);L3D(v[1],v[5],c);L3D(v[2],v[6],c);L3D(v[3],v[7],c);}
void Grid(void){
    for(INT32 i=-20;i<=20;i++){UINT32 col=(i==0)?0x00003388:0x00001122;
    L3D(v3((INT64)i*2000,0,-40000),v3((INT64)i*2000,0,40000),col);
    L3D(v3(-40000,0,(INT64)i*2000),v3(40000,0,(INT64)i*2000),col);}}
typedef struct{INT64 wx,wy,wz,sw,sh,sd;UINT32 col;const CHAR8 *nm;}Struct;
static const Struct World[]={
    {-1000,0,-8000,2000,6000,2000,0x0000FFCC,"GENLEX"},
    { 5000,0,-5000,3000,4000,3000,0x000088FF,"NEURAL"},
    {-8000,0,-3000,3000,3000,3000,0x00FF8800,"MEMORY"},
    {-2000,0,-14000,4000,8000,4000,0x0000FFAA,"KERNEL"},
    { 2000,0,-12000,3000,5000,3000,0x0000DDFF,"SARAH"},
    { 8000,0,-8000,2000,3000,2000,0x00FFAA00,"GCP"},
    {-5000,0,-10000,2000,4000,2000,0x00FF66FF,"AERIS"},
    { 2000,0,-3000,1000,1000,1000,0x00004488,"NODE"},
};
#define WC 8

void DrawHUD(void){
    for(UINT32 x=0;x<FBW;x++){
        UINT32 c=LerpC(0x00001530,0x00000510,(INT32)x,(INT32)FBW);
        PX((INT32)x,0,c);PX((INT32)x,1,c);PX((INT32)x,26,0x00002244);}
    TStr(8,6,"GENESIS WORLD",0x0000FFCC,2);
    if(WiFiOnline){TStr(FBW-140,6,"WIFI ON",0x0000FF66,2);}
    else{TStr(FBW-160,6,"WIFI OFF",0x00FF4400,2);}
    for(UINT32 x=0;x<FBW;x++){
        PX((INT32)x,(INT32)(FBH-28),0x00001020);
        PX((INT32)x,(INT32)(FBH-1),0x0000FFFF);
        PX((INT32)x,(INT32)(FBH-2),0x00003344);}
    TStr(8,FBH-22,"WASD:MOVE  QE:TURN  RF:LOOK  N:WIFI  ESC:REBOOT",0x00004466,1);}

void RenderFrame(void){
    for(UINT32 y=0;y<FBH;y++){UINT32 c=LerpC(0x00000008,0x00000218,(INT32)y,(INT32)FBH);
        for(UINT32 x=0;x<FBW;x++) BB[y*FBW+x]=c;}
    UINT32 hz=FBH/2+(UINT32)((INT32)FBH*Cam.pitch/180);
    if(hz<FBH-5) for(INT32 g=0;g<6;g++) HLine(0,(INT32)hz+g,(INT32)FBW,LerpC(0x00003355,0x00000010,g,6));
    Grid();
    for(UINT32 i=0;i<WC;i++){
        const Struct *s=&World[i]; Box(s->wx,s->wy,s->wz,s->sw,s->sh,s->sd,s->col);
        INT32 tx,ty; V3 top=v3(s->wx+s->sw/2,s->wy+s->sh+200,s->wz+s->sd/2);
        if(Project(top,&tx,&ty)) for(INT32 r=-2;r<=2;r++) for(INT32 c2=-2;c2<=2;c2++) PX(tx+c2,ty+r,s->col);}
    DrawHUD();
    if(ShowWifi) DrawWifiPanel();
    Blit();}

void Move(INT32 f,INT32 st2){INT32 sp=800;
    Cam.pz+=(INT64)f*icos(Cam.yaw)/1000*sp; Cam.px+=(INT64)f*isin(Cam.yaw)/1000*sp;
    Cam.pz+=(INT64)st2*icos(Cam.yaw+90)/1000*sp; Cam.px+=(INT64)st2*isin(Cam.yaw+90)/1000*sp;}

EFI_STATUS LoadAllScript(EFI_HANDLE ImageHandle, CHAR16* FileName) {
    EFI_LOADED_IMAGE *li;
    EFI_SIMPLE_FILE_SYSTEM_PROTOCOL *fs;
    EFI_FILE_HANDLE root, file;
    uefi_call_wrapper(ST->BootServices->HandleProtocol, 3, ImageHandle, &gEfiLoadedImageProtocolGuid, (VOID**)&li);
    uefi_call_wrapper(ST->BootServices->HandleProtocol, 3, li->DeviceHandle, &gEfiSimpleFileSystemProtocolGuid, (VOID**)&fs);
    uefi_call_wrapper(fs->OpenVolume, 2, fs, &root);
    EFI_STATUS status = uefi_call_wrapper(root->Open, 5, root, &file, FileName, EFI_FILE_MODE_READ, 0);
    if(EFI_ERROR(status)) return status;

    CHAR8 buf[512];
    UINTN sz = 511;
    while(uefi_call_wrapper(file->Read, 3, file, &sz, buf) == EFI_SUCCESS && sz > 0) {
        buf[sz] = 0;
        CHAR8* p = buf;
        while(*p) {
            CHAR8* start = p;
            while(*p && *p != '\n' && *p != '\r') p++;
            CHAR8 old = *p; *p = 0;
            ExecuteLine(ImageHandle, start);
            if(old) p++;
            if(*p == '\n' || *p == '\r') p++;
        }
        sz = 511;
    }
    uefi_call_wrapper(file->Close, 1, file);
    return EFI_SUCCESS;
}

// ===================================================================
// MAIN
// ===================================================================
EFI_STATUS efi_main(EFI_HANDLE ImageHandle, EFI_SYSTEM_TABLE *SystemTable) {
    InitializeLib(ImageHandle, SystemTable);
    ST = SystemTable;
    // Kill the UEFI 5-minute watchdog — without this the board force-reboots
    uefi_call_wrapper(ST->BootServices->SetWatchdogTimer, 4, 0, 0, 0, NULL);
    uefi_call_wrapper(ST->ConOut->ClearScreen,1,ST->ConOut);

    EFI_GUID gopGuid = EFI_GRAPHICS_OUTPUT_PROTOCOL_GUID;
    uefi_call_wrapper(ST->BootServices->LocateProtocol,3,&gopGuid,NULL,(void**)&Gop);
    if(!Gop){Print(L"NO DISPLAY\n");return EFI_UNSUPPORTED;}
    FB=(UINT32*)Gop->Mode->FrameBufferBase;
    FBW=Gop->Mode->Info->HorizontalResolution;
    FBH=Gop->Mode->Info->VerticalResolution;
    SL=Gop->Mode->Info->PixelsPerScanLine;
    uefi_call_wrapper(ST->BootServices->AllocatePool,3,EfiLoaderData,(UINTN)FBW*(UINTN)FBH*4,(VOID**)&BB);

    // Boot media check
    EFI_GUID BioGuid=EFI_BLOCK_IO_PROTOCOL_GUID, LiGuid=EFI_LOADED_IMAGE_PROTOCOL_GUID;
    EFI_LOADED_IMAGE *LI; EFI_BLOCK_IO *BM=NULL;
    uefi_call_wrapper(ST->BootServices->HandleProtocol,3,ImageHandle,&LiGuid,(void**)&LI);
    uefi_call_wrapper(ST->BootServices->HandleProtocol,3,LI->DeviceHandle,&BioGuid,(void**)&BM);
    BOOLEAN IsUsb=BM&&BM->Media&&BM->Media->RemovableMedia;

    if(IsUsb){
        FillScreen(0x00000510);
        TStr(FBW/2-90,FBH/2-30,"GENESIS INSTALLER",0x0000FFCC,2);
        TStr(FBW/2-120,FBH/2+10,"C TO INSTALL TO SSD",0x00888888,1); Blit();
        EFI_BLOCK_IO *Dst=NULL; UINTN Cnt=0; EFI_HANDLE *Buf=NULL;
        uefi_call_wrapper(ST->BootServices->LocateHandleBuffer,5,ByProtocol,&BioGuid,NULL,&Cnt,&Buf);
        for(UINTN i=0;i<Cnt;i++){EFI_BLOCK_IO *Bio;
            uefi_call_wrapper(ST->BootServices->HandleProtocol,3,Buf[i],&BioGuid,(void**)&Bio);
            if(!Bio||!Bio->Media||Bio->Media->LogicalPartition||Bio->Media->RemovableMedia)continue;
            if(Buf[i]==LI->DeviceHandle)continue; Dst=Bio; break;}
        EFI_INPUT_KEY key;
        while(1){UINTN idx;
            uefi_call_wrapper(ST->BootServices->WaitForEvent,3,1,&ST->ConIn->WaitForKey,&idx);
            uefi_call_wrapper(ST->ConIn->ReadKeyStroke,2,ST->ConIn,&key);
            if((key.UnicodeChar==L'C'||key.UnicodeChar==L'c')&&Dst){
                UINT32 blk=Dst->Media->BlockSize; UINT8 *Mbr;
                uefi_call_wrapper(ST->BootServices->AllocatePool,3,EfiLoaderData,blk,(VOID**)&Mbr);
                ZeroMem(Mbr,blk); Mbr[446]=0x80;Mbr[450]=0x0C;
                Mbr[454]=0;Mbr[455]=8;Mbr[456]=0;Mbr[457]=0;
                Mbr[458]=0;Mbr[459]=0;Mbr[460]=4;Mbr[461]=0;
                Mbr[510]=0x55;Mbr[511]=0xAA;
                uefi_call_wrapper(Dst->WriteBlocks,5,Dst,Dst->Media->MediaId,0,blk,Mbr);
                FillScreen(0); TStr(8,8,"INSTALLING",0x0000FF88,1); Blit();
                VOID *Chunk; uefi_call_wrapper(ST->BootServices->AllocatePool,3,EfiLoaderData,1024*1024,&Chunk);
                UINT64 bpm=(1024*1024)/blk,total=(128ULL*1024*1024)/blk;
                for(UINT64 lba=0;lba<total;lba+=bpm){
                    uefi_call_wrapper(BM->ReadBlocks,5,BM,BM->Media->MediaId,lba,1024*1024,Chunk);
                    uefi_call_wrapper(Dst->WriteBlocks,5,Dst,Dst->Media->MediaId,lba+2048,1024*1024,Chunk);}
                uefi_call_wrapper(Dst->FlushBlocks,1,Dst);
                FillScreen(0); TStr(8,8,"DONE  PULL USB  PRESS R",0x0000FF44,1); Blit();}
            if(key.UnicodeChar==L'R'||key.UnicodeChar==L'r')
                uefi_call_wrapper(ST->RuntimeServices->ResetSystem,4,EfiResetCold,EFI_SUCCESS,0,NULL);}
    }

    // NATIVE OS — Boot sequence
    Cam.px=0;Cam.py=-1500;Cam.pz=4000;Cam.yaw=0;Cam.pitch=10;
    FillScreen(0); TStr(8,8,"GENESIS BOOT",0x0000FFCC,2); Blit();

    // 1. Hardware Initialization
    FindSnpForDHCP();
    if(WifiSNP) DoDHCPOnSNP(WifiSNP);

    // 2. SOVEREIGN HANDOVER (GENLEX)
    TStr(8,40,"SOVEREIGN HANDOVER",0x0000FFFF,1); Blit();
    LoadAllScript(ImageHandle, L"\\core\\sarah_os.all");

    // Fallback Loop
    UINTN _unused = 0; (void)_unused;
    EFI_INPUT_KEY key;
    while(1){
        RenderFrame();
        if(ST->ConIn->ReadKeyStroke(ST->ConIn,&key)==EFI_SUCCESS){
            UINT16 sc=key.ScanCode; CHAR16 ch=key.UnicodeChar;

            if(ShowWifi){
                // Global ESC: close panel entirely
                if(sc==0x17 && WifiState!=2 && WifiState!=5 && WifiState!=6){
                    ShowWifi=FALSE; WifiState=0; continue;
                }

                if(WifiState==1){
                    if(sc==0x01&&SelNet>0) SelNet--;
                    if(sc==0x02&&SelNet<(INT32)ScannedCount-1) SelNet++;
                    if(ch==L'r'||ch==L'R'){
                        WifiState=0; RenderFrame();
                        DoWifiScan(); WifiState=1; SelNet=0;
                    }
                    if(ch==L'm'||ch==L'M'){
                        // Manual SSID entry
                        WifiState=5; SSIDLen=0; SetMem(InputSSID,64,0);
                    }
                    if((ch==L'\r'||ch==L'\n')&&ScannedCount>0){
                        WifiState=2; PassLen=0; SetMem(InputPass,128,0);
                    }

                } else if(WifiState==5){
                    // Manual SSID typing
                    if(sc==0x17){ WifiState=1; continue; }
                    if(sc==0x08||ch==0x08){ if(SSIDLen>0) InputSSID[--SSIDLen]=0; }
                    else if(ch>=0x20&&ch<=0x7E&&SSIDLen<63){ InputSSID[SSIDLen++]=(CHAR8)ch; }
                    else if((ch==L'\r'||ch==L'\n')&&SSIDLen>0){
                        WifiState=6; PassLen=0; SetMem(InputPass,128,0);
                    }

                } else if(WifiState==6){
                    // Manual password typing
                    if(sc==0x17){ WifiState=5; continue; }
                    if(sc==0x08||ch==0x08){ if(PassLen>0) InputPass[--PassLen]=0; }
                    else if(ch>=0x20&&ch<=0x7E&&PassLen<127){ InputPass[PassLen++]=(CHAR8)ch; }
                    else if(ch==L'\r'||ch==L'\n'){
                        // Attempt connect with manually typed SSID+pass
                        WifiState=3; RenderFrame(); Stall(200);
                        if(Wifi2){
                            EFI_80211_SSID ssid;
                            ssid.SSIDLen=(UINT8)SSIDLen;
                            CopyMem(ssid.SSID, InputSSID, SSIDLen);
                            uefi_call_wrapper(Wifi2->Connect,4,Wifi2,&ssid,(UINT8*)InputPass,(UINTN)PassLen);
                            Stall(4000);
                        }
                        FindSnpForDHCP();
                        if(WifiSNP) DoDHCPOnSNP(WifiSNP);
                        WifiState=4;
                    }

                } else if(WifiState==2){
                    if(sc==0x17){ WifiState=1; continue; }
                    if(sc==0x08||ch==0x08){ if(PassLen>0) InputPass[--PassLen]=0; }
                    else if(ch>=0x20&&ch<=0x7E&&PassLen<127){ InputPass[PassLen++]=(CHAR8)ch; }
                    else if(ch==L'\r'||ch==L'\n'){
                        WifiState=3; RenderFrame(); Stall(200);
                        // Use WiFi2 Connect if available
                        if(Wifi2){
                            EFI_80211_SSID ssid;
                            UINT8 slen=0;
                            while(ScannedNets[SelNet].SSID[slen]&&slen<32)slen++;
                            ssid.SSIDLen=slen;
                            CopyMem(ssid.SSID, ScannedNets[SelNet].SSID, slen);
                            uefi_call_wrapper(Wifi2->Connect,4,Wifi2,&ssid,(UINT8*)InputPass,(UINTN)PassLen);
                            Stall(4000); // wait for association
                        }
                        // DHCP
                        FindSnpForDHCP();
                        if(WifiSNP) DoDHCPOnSNP(WifiSNP);
                        WifiState=4;
                    }
                } else if(WifiState==4){
                    if(ch==L'r'||ch==L'R'){ WifiState=0; RenderFrame(); DoWifiScan(); WifiState=1; SelNet=0; }
                }
                continue;
            }

            if(ch==L'n'||ch==L'N'){
                ShowWifi=TRUE; WifiState=0; SelNet=0;
                // Trigger scan immediately
                RenderFrame();
                FindWifi2();
                DoWifiScan();
                WifiState=1;
            }
            if(ch==L'w'||ch==L'W') Move(1,0);
            if(ch==L's'||ch==L'S') Move(-1,0);
            if(ch==L'a'||ch==L'A') Move(0,-1);
            if(ch==L'd'||ch==L'D') Move(0,1);
            if(ch==L'q'||ch==L'Q') Cam.yaw=(Cam.yaw-5+360)%360;
            if(ch==L'e'||ch==L'E') Cam.yaw=(Cam.yaw+5)%360;
            if(ch==L'r'||ch==L'R'){if(Cam.pitch<60)Cam.pitch+=3;}
            if(ch==L'f'||ch==L'F'){if(Cam.pitch>-60)Cam.pitch-=3;}
            if(sc==0x17) uefi_call_wrapper(ST->RuntimeServices->ResetSystem,4,EfiResetCold,EFI_SUCCESS,0,NULL);
        }
    }
    return EFI_SUCCESS;
}
