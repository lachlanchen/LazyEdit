package art.lazying.lazyedit;

import android.app.Activity;
import android.os.Handler;
import android.os.Looper;
import com.android.billingclient.api.*;
import org.json.*;
import java.util.*;
import java.util.concurrent.*;

/** One bounded native billing connection. Server verification grants service. */
final class StudioBilling implements PurchasesUpdatedListener, AutoCloseable {
    interface Display { void product(String label,Runnable buy); void message(String text); }
    private final Activity activity;
    private final StudioApi api;
    private final Display display;
    private final String context,accountToken;
    private final BillingClient client;
    private final Handler ui=new Handler(Looper.getMainLooper());
    private final ExecutorService worker=Executors.newSingleThreadExecutor();
    private volatile boolean closed=false;
    private final Runnable timeout;
    StudioBilling(Activity activity,StudioApi api,JSONObject catalog,Display display) {
        this.activity=activity;this.api=api;this.display=display;context=api.scope();accountToken=catalog.optString("accountToken");
        timeout=()->{if(!closed){display.message("Store connection timed out. Open billing again to retry.");close();}};
        client=BillingClient.newBuilder(activity).setListener(this).enablePendingPurchases(PendingPurchasesParams.newBuilder().enableOneTimeProducts().build()).enableAutoServiceReconnection().build();
        ui.postDelayed(timeout,20000);
        client.startConnection(new BillingClientStateListener(){
            public void onBillingServiceDisconnected(){if(valid())display.message("Store connection interrupted. Open billing again to retry.");}
            public void onBillingSetupFinished(BillingResult result){
                if(!valid())return;
                if(result.getResponseCode()!=BillingClient.BillingResponseCode.OK){ui.removeCallbacks(timeout);display.message("Store products are not available yet.");return;}
                try {
                    List<QueryProductDetailsParams.Product> products=new ArrayList<>();JSONArray plans=catalog.getJSONArray("plans");
                    for(int i=0;i<plans.length();i++)products.add(QueryProductDetailsParams.Product.newBuilder().setProductId(plans.getJSONObject(i).getString("product")).setProductType(BillingClient.ProductType.SUBS).build());
                    client.queryProductDetailsAsync(QueryProductDetailsParams.newBuilder().setProductList(products).build(),(reply,data)->{
                        ui.removeCallbacks(timeout);if(!valid())return;
                        if(reply.getResponseCode()!=BillingClient.BillingResponseCode.OK||data.getProductDetailsList().isEmpty()){display.message("Store products are not available yet.");return;}
                        for(ProductDetails product:data.getProductDetailsList()) {
                            if(product.getSubscriptionOfferDetails()==null)continue;
                            for(ProductDetails.SubscriptionOfferDetails offer:product.getSubscriptionOfferDetails()){
                                if(offer.getOfferId()!=null)continue; // No unverified paid-download discount.
                                List<ProductDetails.PricingPhase> phases=offer.getPricingPhases().getPricingPhaseList();
                                if(phases.isEmpty()||!phases.get(phases.size()-1).getBillingPeriod().equals("P1M"))continue;
                                display.product(product.getName()+" · "+phases.get(phases.size()-1).getFormattedPrice(),()->buy(product,offer.getOfferToken()));break;
                            }
                        }
                    });
                }catch(Exception error){display.message("Store products are not available yet.");}
            }
        });
    }
    private boolean valid(){return !closed&&!activity.isDestroyed()&&api.signedIn()&&context.equals(api.scope());}
    private void buy(ProductDetails product,String offer) {
        if(!valid())return;
        BillingResult result=client.launchBillingFlow(activity,BillingFlowParams.newBuilder().setObfuscatedAccountId(accountToken).setProductDetailsParamsList(Collections.singletonList(BillingFlowParams.ProductDetailsParams.newBuilder().setProductDetails(product).setOfferToken(offer).build())).build());
        if(result.getResponseCode()!=BillingClient.BillingResponseCode.OK)display.message("Store request could not finish.");
    }
    public void onPurchasesUpdated(BillingResult result,List<Purchase> purchases) {
        if(!valid())return;
        if(result.getResponseCode()==BillingClient.BillingResponseCode.USER_CANCELED)return;
        if(result.getResponseCode()!=BillingClient.BillingResponseCode.OK||purchases==null){display.message("Store request could not finish.");return;}
        for(Purchase purchase:purchases)verify(purchase);
    }
    private void verify(Purchase purchase) {
        if(purchase.getPurchaseState()!=Purchase.PurchaseState.PURCHASED){display.message("Waiting for payment confirmation");return;}
        worker.execute(()->{
            if(!valid())return;
            try {
                api.post("/accounts/billing/verify",new JSONObject().put("provider","google").put("purchaseToken",purchase.getPurchaseToken()));
                ui.post(()->{if(valid())display.message("Purchase verified for your Studio account.");});
            }catch(Exception error){ui.post(()->{if(valid())display.message("Purchase verification is pending. Use Restore purchases to retry.");});}
        });
    }
    void restore() {
        if(!valid()||!client.isReady())return;
        client.queryPurchasesAsync(QueryPurchasesParams.newBuilder().setProductType(BillingClient.ProductType.SUBS).build(),(result,purchases)->{
            if(!valid())return;
            if(result.getResponseCode()==BillingClient.BillingResponseCode.OK)for(Purchase purchase:purchases)verify(purchase);
            else display.message("Store request could not finish.");
        });
    }
    public void close(){closed=true;ui.removeCallbacks(timeout);client.endConnection();worker.shutdown();}
}
